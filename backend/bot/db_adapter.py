"""
Database Adapter for Masii Bot
Handles all database operations for onboarding session and user data
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional, Any, List
import psycopg2
from psycopg2.extras import RealDictCursor, Json
import os

logger = logging.getLogger(__name__)


class DatabaseAdapter:
    """
    Adapter for Masii Supabase Postgres database.
    Handles session state, user data, and onboarding answers.
    """
    
    def __init__(self, database_url: str = None):
        """Initialize database connection"""
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL not set")
        
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor
            )
            self.conn.autocommit = True
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def _execute(self, query: str, params: tuple = None, fetch: bool = False) -> Any:
        """Execute a database query with error handling"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall() if cur.rowcount > 1 else cur.fetchone()
                return cur.rowcount
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            
            # Try to reconnect
            try:
                self._connect()
            except:
                pass
            
            raise
    
    # ============== SESSION MANAGEMENT ==============
    
    def get_session(self, telegram_id: int) -> Optional[Dict]:
        """
        Retrieve onboarding session state for a user.
        Returns None if no session exists.
        """
        query = """
            SELECT session_data, last_active
            FROM conversation_state
            WHERE user_id = %s
        """
        
        result = self._execute(query, (telegram_id,), fetch=True)
        
        if result:
            return {
                'user_id': telegram_id,
                **result['session_data'],
                'last_active': result['last_active'].isoformat() if result['last_active'] else None
            }
        
        return None
    
    def save_session(self, session: Dict):
        """
        Save or update onboarding session state.
        Uses upsert to handle both new and existing sessions.
        """
        user_id = session['user_id']
        
        # Extract fields
        session_data = {
            k: v for k, v in session.items()
            if k not in ['user_id', 'last_active']
        }
        
        query = """
            INSERT INTO conversation_state (user_id, session_data, last_active)
            VALUES (%s, %s, NOW())
            ON CONFLICT (user_id)
            DO UPDATE SET
                session_data = EXCLUDED.session_data,
                last_active = EXCLUDED.last_active
        """
        
        self._execute(query, (user_id, Json(session_data)))
        logger.debug(f"Session saved for user {user_id}")
    
    def clear_session(self, telegram_id: int):
        """Delete session state (for restart)"""
        query = "DELETE FROM conversation_state WHERE user_id = %s"
        self._execute(query, (telegram_id,))
        logger.info(f"Session cleared for user {telegram_id}")
    
    # ============== USER DATA ==============
    
    def get_user(self, telegram_id: int) -> Optional[Dict]:
        """Get user record"""
        query = "SELECT * FROM users WHERE telegram_id = %s"
        return self._execute(query, (telegram_id,), fetch=True)
    
    def create_user(self, telegram_id: int, username: str = None, first_name: str = None):
        """Create new user record"""
        query = """
            INSERT INTO users (telegram_id, username, first_name, created_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (telegram_id) DO NOTHING
        """
        self._execute(query, (telegram_id, username, first_name))
        logger.info(f"User created: {telegram_id}")
    
    async def save_answer(self, telegram_id: int, table: str, field: str, value: Any):
        """
        Save a single answer to the appropriate database table.
        Handles users, preferences, and signals tables.
        """
        if table == 'users':
            await self._save_to_users_table(telegram_id, field, value)
        elif table == 'preferences':
            await self._save_to_preferences_table(telegram_id, field, value)
        elif table in ('signals', 'personality'):
            await self._save_to_jsonb_table('user_signals', telegram_id, field, value)
    
    async def _save_to_users_table(self, telegram_id: int, field: str, value: Any):
        """Save answer to users table column"""
        # Map field names to actual column names
        # Covers both the old 79-Q fields and the new 36-guna fields
        column_map = {
            # Identity & basics
            'first_name': 'first_name',
            'date_of_birth': 'date_of_birth',
            'gender_identity': 'gender_identity',
            'looking_for_gender': 'looking_for_gender',
            'marital_status': 'marital_status',
            'children_existing': 'children_existing',
            'relationship_intent': 'relationship_intent',
            # Location
            'country_current': 'country_current',
            'state_india': 'state_india',
            'city_current': 'city_current',
            'willing_to_relocate': 'willing_to_relocate',
            # Religion & culture
            'religion': 'religion',
            'religious_practice': 'religious_practice',
            'sect_denomination': 'sect_denomination',
            'caste_community': 'caste_community',
            'mother_tongue': 'mother_tongue',
            # Family
            'family_type': 'family_type',
            'family_involvement_search': 'family_involvement_search',
            'living_with_parents_post_marriage': 'living_with_parents_post_marriage',
            'children_intent': 'children_intent',
            'children_timeline': 'children_timeline',
            # Lifestyle
            'diet': 'diet',
            'drinking': 'drinking',
            'smoking': 'smoking',
            'education_level': 'education_level',
            'work_industry': 'work_industry',
            'career_ambition': 'career_ambition',
            'social_style': 'social_style',
            # Legacy fields (kept for backward compatibility)
            'height_cm': 'height_cm',
            'body_type': 'body_type',
            'complexion': 'complexion',
            'residency_type': 'residency_type',
            'hometown_state': 'hometown_state',
            'settling_country': 'settling_country',
            'sub_caste': 'sub_caste',
            'languages_spoken': 'languages_spoken',
            'manglik_status': 'manglik_status',
        }
        
        column = column_map.get(field, field)
        
        # Build update query
        query = f"""
            UPDATE users
            SET {column} = %s, updated_at = NOW()
            WHERE telegram_id = %s
        """
        
        self._execute(query, (value, telegram_id))
        logger.debug(f"Saved {field} = {value} for user {telegram_id}")
    
    async def _save_to_preferences_table(self, telegram_id: int, field: str, value: Any):
        """Save answer to user_preferences table column"""
        # First get user_id from telegram_id
        user_id_query = "SELECT id FROM users WHERE telegram_id = %s"
        result = self._execute(user_id_query, (telegram_id,), fetch=True)
        if not result:
            logger.error(f"User not found for telegram_id {telegram_id}")
            return
        
        # result is a dict-like RealDictRow, not a list
        user_id = result['id']
        
        # Ensure row exists in user_preferences
        create_query = """
            INSERT INTO user_preferences (user_id)
            VALUES (%s)
            ON CONFLICT (user_id) DO NOTHING
        """
        self._execute(create_query, (user_id,))
        
        # Column mapping for user_preferences table
        column_map = {
            'partner_location_pref': 'partner_location_pref',
            'partner_religion_pref': 'partner_religion_pref',
            'caste_importance': 'caste_importance',
            'partner_diet_pref': 'partner_diet_pref',
            'smoking_partner_ok': 'smoking_partner_ok',
            'drinking_partner_ok': 'drinking_partner_ok',
            'pref_age_range': 'pref_age_range',
            'pref_height': 'pref_height',
            'pref_complexion': 'pref_complexion',
            'pref_education_min': 'pref_education_min',
            'pref_income_range': 'pref_income_range',
            'pref_marital_status': 'pref_marital_status',
            'pref_children_ok': 'pref_children_ok',
            'pref_disability_ok': 'pref_disability_ok',
            'pref_working_spouse': 'pref_working_spouse',
            'db_divorced_ok': 'db_divorced_ok',
            'db_widowed_ok': 'db_widowed_ok',
            'db_children_ok': 'db_children_ok',
            'db_nri_ok': 'db_nri_ok',
            'db_age_gap_max': 'db_age_gap_max',
        }
        
        column = column_map.get(field, field)
        
        # Build update query
        query = f"""
            UPDATE user_preferences
            SET {column} = %s, updated_at = NOW()
            WHERE user_id = %s
        """
        
        self._execute(query, (value, user_id))
        logger.debug(f"Saved {field} = {value} to user_preferences for user {user_id}")
    
    async def _save_to_jsonb_table(self, table: str, telegram_id: int, field: str, value: Any):
        """Save answer to JSONB column in preferences or signals table"""
        # Get user_id from telegram_id (both tables reference users.id, not telegram_id)
        user_id_query = "SELECT id FROM users WHERE telegram_id = %s"
        result = self._execute(user_id_query, (telegram_id,), fetch=True)
        if not result:
            logger.error(f"User not found for telegram_id {telegram_id}")
            return
        
        user_id = result['id']
        
        # First, ensure row exists
        if table == 'user_preferences':
            create_query = """
                INSERT INTO user_preferences (user_id, preferences)
                VALUES (%s, '{}'::jsonb)
                ON CONFLICT (user_id) DO NOTHING
            """
        else:  # user_signals
            create_query = """
                INSERT INTO user_signals (user_id, signals)
                VALUES (%s, '{}'::jsonb)
                ON CONFLICT (user_id) DO NOTHING
            """
        
        self._execute(create_query, (user_id,))
        
        # Update JSONB field
        column = 'preferences' if table == 'user_preferences' else 'signals'
        
        query = f"""
            UPDATE {table}
            SET {column} = {column} || %s::jsonb,
                updated_at = NOW()
            WHERE user_id = %s
        """
        
        jsonb_value = json.dumps({field: value})
        self._execute(query, (jsonb_value, user_id))
        logger.debug(f"Saved {field} to {table}.{column} for user {user_id}")
    
    # ============== PHOTO STORAGE ==============
    
    def save_photo_url(self, telegram_id: int, photo_url: str, photo_type: str = 'profile'):
        """Save photo URL to database"""
        query = """
            INSERT INTO user_photos (user_id, photo_url, photo_type, uploaded_at)
            VALUES (%s, %s, %s, NOW())
        """
        self._execute(query, (telegram_id, photo_url, photo_type))
        logger.info(f"Photo saved for user {telegram_id}")
    
    def get_photos(self, telegram_id: int) -> List[Dict]:
        """Get all photos for a user"""
        query = """
            SELECT photo_url, photo_type, uploaded_at
            FROM user_photos
            WHERE user_id = %s
            ORDER BY uploaded_at DESC
        """
        return self._execute(query, (telegram_id,), fetch=True) or []
    
    # ============== PROFILE COMPLETION ==============
    
    def get_profile_completion(self, telegram_id: int) -> Dict:
        """
        Calculate profile completion status.
        Returns dict with completion percentage and missing fields.
        """
        # Get user data
        user = self.get_user(telegram_id)
        if not user:
            return {"completion": 0, "missing": []}
        
        # Required fields for Tier 1 (basic profile)
        tier1_fields = [
            'gender_identity', 'looking_for_gender', 'date_of_birth',
            'city_current', 'religion', 'children_intent', 'marital_status',
            'smoking', 'drinking', 'relationship_intent'
        ]
        
        # Check which fields are filled
        filled = sum(1 for field in tier1_fields if user.get(field))
        total = len(tier1_fields)
        
        missing = [field for field in tier1_fields if not user.get(field)]
        
        completion_pct = (filled / total * 100) if total > 0 else 0
        
        return {
            "completion": round(completion_pct, 1),
            "filled_count": filled,
            "total_count": total,
            "missing": missing
        }
    
    # ============== WEB FORM INTAKE ==============

    def get_or_create_user_by_phone(self, phone: str, name: str = "", channel: str = "web") -> int:
        """
        Find existing user by phone or create a new one.
        Returns the user's id (UUID from users table).
        """
        # Check if user exists by phone
        query = "SELECT id FROM users WHERE phone = %s LIMIT 1"
        result = self._execute(query, (phone,), fetch=True)

        if result:
            user_id = result['id']
        else:
            # Create new user with phone and name
            query = """
                INSERT INTO users (phone, first_name, created_at, updated_at)
                VALUES (%s, %s, NOW(), NOW())
                RETURNING id
            """
            result = self._execute(query, (phone, name or None), fetch=True)
            user_id = result['id']
            logger.info(f"Created new user via web form: {user_id}")

        # Ensure user_channels entry exists
        channel_query = """
            INSERT INTO user_channels (user_id, channel, channel_user_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, channel) DO NOTHING
        """
        self._execute(channel_query, (user_id, channel, phone))

        return user_id

    def save_web_intake(self, user_id, answers: Dict, meta: Dict = None):
        """
        Bulk save all answers from the web form.
        answers format: { field_name: { value: "...", table: "users|preferences|signals" } }
        """
        # Column mappings (same as used in save_answer methods)
        users_columns = {
            'first_name', 'date_of_birth', 'gender_identity', 'looking_for_gender',
            'marital_status', 'children_existing', 'relationship_intent',
            'country_current', 'state_india', 'city_current', 'willing_to_relocate',
            'religion', 'religious_practice', 'sect_denomination', 'caste_community',
            'mother_tongue', 'family_type', 'family_involvement_search',
            'living_with_parents_post_marriage', 'children_intent', 'children_timeline',
            'diet', 'drinking', 'smoking', 'education_level', 'work_industry',
            'career_ambition', 'social_style',
        }

        preferences_columns = {
            'partner_location_pref', 'partner_religion_pref', 'caste_importance',
            'partner_diet_pref',
        }

        signals_fields = {}
        users_updates = {}
        preferences_updates = {}

        for field, info in answers.items():
            value = info.get('value') if isinstance(info, dict) else info
            table = info.get('table', 'users') if isinstance(info, dict) else 'users'

            if table == 'users' and field in users_columns:
                users_updates[field] = value
            elif table == 'preferences' and field in preferences_columns:
                preferences_updates[field] = value
            elif table in ('signals', 'personality'):
                signals_fields[field] = value

        # Batch update users table
        if users_updates:
            set_clauses = ", ".join(f"{col} = %s" for col in users_updates.keys())
            values = list(users_updates.values()) + [user_id]
            query = f"UPDATE users SET {set_clauses}, updated_at = NOW() WHERE id = %s"
            self._execute(query, tuple(values))

        # Ensure preferences row exists, then update
        if preferences_updates:
            self._execute(
                "INSERT INTO user_preferences (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING",
                (user_id,)
            )
            set_clauses = ", ".join(f"{col} = %s" for col in preferences_updates.keys())
            values = list(preferences_updates.values()) + [user_id]
            query = f"UPDATE user_preferences SET {set_clauses}, updated_at = NOW() WHERE user_id = %s"
            self._execute(query, tuple(values))

        # Save signals as JSONB merge
        if signals_fields:
            self._execute(
                "INSERT INTO user_signals (user_id, signals) VALUES (%s, '{}'::jsonb) ON CONFLICT (user_id) DO NOTHING",
                (user_id,)
            )
            query = """
                UPDATE user_signals
                SET signals = signals || %s::jsonb, updated_at = NOW()
                WHERE user_id = %s
            """
            self._execute(query, (json.dumps(signals_fields), user_id))

        # Save meta (intent, proxy info) to signals if present
        if meta and any(v for v in meta.values() if v is not None):
            meta_clean = {k: v for k, v in meta.items() if v is not None}
            self._execute(
                "INSERT INTO user_signals (user_id, signals) VALUES (%s, '{}'::jsonb) ON CONFLICT (user_id) DO NOTHING",
                (user_id,)
            )
            query = """
                UPDATE user_signals
                SET signals = signals || %s::jsonb, updated_at = NOW()
                WHERE user_id = %s
            """
            self._execute(query, (json.dumps({"web_meta": meta_clean}), user_id))

        logger.info(f"Web intake saved: {len(users_updates)} user fields, "
                     f"{len(preferences_updates)} pref fields, "
                     f"{len(signals_fields)} signal fields for user {user_id}")

    # ============== UTILITY ==============

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
