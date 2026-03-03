"""
Database Adapter for Masii Bot
Handles all database operations for onboarding session and user data.
Column names aligned with docs/question-flow.md and migration 13.
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

            try:
                self._connect()
            except:
                pass

            raise

    # ============== SESSION MANAGEMENT ==============

    def get_session(self, telegram_id: int) -> Optional[Dict]:
        """Retrieve onboarding session state for a user."""
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
        """Save or update onboarding session state."""
        user_id = session['user_id']
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
            INSERT INTO users (telegram_id, username, full_name, created_at)
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
        elif table == 'signals':
            await self._save_to_signals_table(telegram_id, field, value)
        elif table == 'meta':
            # Meta fields (like sensitive_gate) are stored in session only
            pass

    async def _save_to_users_table(self, telegram_id: int, field: str, value: Any):
        """Save answer to users table column"""
        # Column map: field name → actual column name
        # All fields from question-flow.md that go to users table
        column_map = {
            # Setup
            'full_name': 'full_name',
            'gender': 'gender',
            # Basics
            'date_of_birth': 'date_of_birth',
            'country_current': 'country_current',
            'state_india': 'state_india',
            'city_current': 'city_current',
            'hometown_state': 'hometown_state',
            'hometown_city': 'hometown_city',
            'mother_tongue': 'mother_tongue',
            'languages_spoken': 'languages_spoken',
            'marital_status': 'marital_status',
            'children_existing': 'children_existing',
            'height_cm': 'height_cm',
            'weight_kg': 'weight_kg',
            # Background
            'religion': 'religion',
            # Education & Career
            'education_level': 'education_level',
            'education_field': 'education_field',
            'occupation_sector': 'occupation_sector',
            'annual_income': 'annual_income',
            # Family
            'family_type': 'family_type',
            'family_status': 'family_status',
            'father_occupation': 'father_occupation',
            'mother_occupation': 'mother_occupation',
            'siblings': 'siblings',
            # Sensitive
            'known_conditions': 'known_conditions',
        }

        column = column_map.get(field)
        if not column:
            logger.warning(f"Unknown users field: {field}")
            return

        # Handle array fields (languages_spoken is TEXT[])
        if field == 'languages_spoken' and isinstance(value, list):
            query = f"""
                UPDATE users
                SET {column} = %s::text[], updated_at = NOW()
                WHERE telegram_id = %s
            """
            self._execute(query, (value, telegram_id))
        # Handle int fields
        elif field in ('height_cm', 'weight_kg'):
            query = f"""
                UPDATE users
                SET {column} = %s::int, updated_at = NOW()
                WHERE telegram_id = %s
            """
            self._execute(query, (value, telegram_id))
        else:
            query = f"""
                UPDATE users
                SET {column} = %s, updated_at = NOW()
                WHERE telegram_id = %s
            """
            self._execute(query, (value, telegram_id))

        logger.debug(f"Saved {field} = {value} for user {telegram_id}")

    async def _save_to_preferences_table(self, telegram_id: int, field: str, value: Any):
        """Save answer to user_preferences table column"""
        user_id_query = "SELECT id FROM users WHERE telegram_id = %s"
        result = self._execute(user_id_query, (telegram_id,), fetch=True)
        if not result:
            logger.error(f"User not found for telegram_id {telegram_id}")
            return

        user_id = result['id']

        # Ensure row exists
        self._execute(
            "INSERT INTO user_preferences (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING",
            (user_id,)
        )

        # Column map for user_preferences table
        column_map = {
            # Background (moved from users per migration 13)
            'religious_practice': 'religious_practice',
            'sect_denomination': 'sect_denomination',
            'caste_community': 'caste_community',
            'caste_importance': 'caste_importance',
            # Partner Background Preferences
            'pref_religion': 'pref_religion',
            'pref_religion_exclude': 'pref_religion_exclude',
            'pref_caste': 'pref_caste',
            'pref_caste_exclude': 'pref_caste_exclude',
            'pref_mother_tongue': 'pref_mother_tongue',
            # Education prefs
            'pref_education_min': 'pref_education_min',
            'pref_income_min': 'pref_income_min',
            # Lifestyle prefs
            'pref_diet': 'pref_diet',
            'pref_drinking': 'pref_drinking',
            'pref_smoking': 'pref_smoking',
            # Marriage & Living
            'marriage_timeline': 'marriage_timeline',
            'children_intent': 'children_intent',
            'children_timeline': 'children_timeline',
            'living_arrangement': 'living_arrangement',
            'relocation_willingness': 'relocation_willingness',
            'family_involvement': 'family_involvement',
            # Partner Physical
            'pref_age_min': 'pref_age_min',
            'pref_age_max': 'pref_age_max',
            'pref_height_min': 'pref_height_min',
            'pref_height_max': 'pref_height_max',
            # Household (Male only)
            'partner_working': 'partner_working',
            # Household (Female only)
            'pref_partner_cooking': 'pref_partner_cooking',
            'pref_partner_household': 'pref_partner_household',
            # Sensitive
            'pref_manglik': 'pref_manglik',
            'pref_gotra_exclude': 'pref_gotra_exclude',
            'pref_family_status': 'pref_family_status',
            'pref_conditions': 'pref_conditions',
        }

        column = column_map.get(field)
        if not column:
            logger.warning(f"Unknown preferences field: {field}")
            return

        # Handle array fields (TEXT[])
        if field in ('pref_religion_exclude', 'pref_caste_exclude', 'pref_gotra_exclude') and isinstance(value, list):
            query = f"""
                UPDATE user_preferences
                SET {column} = %s::text[], updated_at = NOW()
                WHERE user_id = %s
            """
            self._execute(query, (value, user_id))
        # Handle int fields
        elif field in ('pref_age_min', 'pref_age_max', 'pref_height_min', 'pref_height_max'):
            query = f"""
                UPDATE user_preferences
                SET {column} = %s::int, updated_at = NOW()
                WHERE user_id = %s
            """
            self._execute(query, (value, user_id))
        else:
            query = f"""
                UPDATE user_preferences
                SET {column} = %s, updated_at = NOW()
                WHERE user_id = %s
            """
            self._execute(query, (value, user_id))

        logger.debug(f"Saved {field} = {value} to user_preferences for user {user_id}")

    async def _save_to_signals_table(self, telegram_id: int, field: str, value: Any):
        """Save answer to user_signals table as a flat column"""
        user_id_query = "SELECT id FROM users WHERE telegram_id = %s"
        result = self._execute(user_id_query, (telegram_id,), fetch=True)
        if not result:
            logger.error(f"User not found for telegram_id {telegram_id}")
            return

        user_id = result['id']

        # Ensure row exists
        self._execute(
            "INSERT INTO user_signals (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING",
            (user_id,)
        )

        # Column map for user_signals flat columns (per migration 13)
        column_map = {
            'diet': 'diet',
            'drinking': 'drinking',
            'smoking': 'smoking',
            'fitness_frequency': 'fitness_frequency',
            'social_style': 'social_style',
            'conflict_style': 'conflict_style',
            'family_values': 'family_values',
            'financial_planning': 'financial_planning',
            'manglik_status': 'manglik_status',
            'gotra': 'gotra',
            'family_property': 'family_property',
            # Gender-forked: Men
            'cooking_contribution': 'cooking_contribution',
            'household_contribution': 'household_contribution',
            # Gender-forked: Women
            'do_you_cook': 'do_you_cook',
            'career_after_marriage': 'career_after_marriage',
            'financial_contribution': 'financial_contribution',
            'live_with_inlaws': 'live_with_inlaws',
        }

        column = column_map.get(field)
        if not column:
            logger.warning(f"Unknown signals field: {field}")
            return

        query = f"""
            UPDATE user_signals
            SET {column} = %s, updated_at = NOW()
            WHERE user_id = %s
        """
        self._execute(query, (value, user_id))
        logger.debug(f"Saved {field} = {value} to user_signals for user {user_id}")

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
        """Calculate profile completion status."""
        user = self.get_user(telegram_id)
        if not user:
            return {"completion": 0, "missing": []}

        # Required fields aligned to question-flow.md
        required_fields = [
            'full_name', 'gender', 'date_of_birth',
            'city_current', 'religion', 'marital_status',
            'height_cm', 'mother_tongue',
            'education_level', 'occupation_sector',
        ]

        filled = sum(1 for field in required_fields if user.get(field))
        total = len(required_fields)
        missing = [field for field in required_fields if not user.get(field)]

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
        query = "SELECT id FROM users WHERE phone = %s LIMIT 1"
        result = self._execute(query, (phone,), fetch=True)

        if result:
            user_id = result['id']
        else:
            query = """
                INSERT INTO users (phone, full_name, created_at, updated_at)
                VALUES (%s, %s, NOW(), NOW())
                RETURNING id
            """
            result = self._execute(query, (phone, name or None), fetch=True)
            user_id = result['id']
            logger.info(f"Created new user via web form: {user_id}")

        # Ensure user_channels entry exists
        channel_query = """
            INSERT INTO user_channels (user_id, channel, channel_id)
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
        # Column sets aligned to migration 13
        users_columns = {
            'full_name', 'gender', 'date_of_birth',
            'country_current', 'state_india', 'city_current',
            'hometown_state', 'hometown_city',
            'mother_tongue', 'languages_spoken',
            'marital_status', 'children_existing',
            'height_cm', 'weight_kg',
            'religion',
            'education_level', 'education_field',
            'occupation_sector', 'annual_income',
            'family_type', 'family_status',
            'father_occupation', 'mother_occupation', 'siblings',
            'known_conditions',
        }

        preferences_columns = {
            'religious_practice', 'sect_denomination',
            'caste_community', 'caste_importance',
            'pref_religion', 'pref_religion_exclude',
            'pref_caste', 'pref_caste_exclude',
            'pref_mother_tongue',
            'pref_education_min', 'pref_income_min',
            'pref_diet', 'pref_drinking', 'pref_smoking',
            'marriage_timeline', 'children_intent', 'children_timeline',
            'living_arrangement', 'relocation_willingness', 'family_involvement',
            'pref_age_min', 'pref_age_max',
            'pref_height_min', 'pref_height_max',
            'partner_working',
            'pref_partner_cooking', 'pref_partner_household',
            'pref_manglik', 'pref_gotra_exclude',
            'pref_family_status', 'pref_conditions',
        }

        signals_columns = {
            'diet', 'drinking', 'smoking', 'fitness_frequency',
            'social_style', 'conflict_style',
            'family_values', 'financial_planning',
            'manglik_status', 'gotra', 'family_property',
            'cooking_contribution', 'household_contribution',
            'do_you_cook', 'career_after_marriage',
            'financial_contribution', 'live_with_inlaws',
        }

        users_updates = {}
        preferences_updates = {}
        signals_updates = {}

        # Fields that are TEXT[] arrays
        array_fields = {'languages_spoken', 'pref_religion_exclude', 'pref_caste_exclude', 'pref_gotra_exclude'}
        # Fields that are INT
        int_fields = {'height_cm', 'weight_kg', 'pref_age_min', 'pref_age_max', 'pref_height_min', 'pref_height_max'}

        for field, info in answers.items():
            value = info.get('value') if isinstance(info, dict) else info
            table = info.get('table', 'users') if isinstance(info, dict) else 'users'

            if table == 'users' and field in users_columns:
                users_updates[field] = value
            elif table == 'preferences' and field in preferences_columns:
                preferences_updates[field] = value
            elif table == 'signals' and field in signals_columns:
                signals_updates[field] = value

        # Batch update users table
        if users_updates:
            set_clauses = []
            values = []
            for col, val in users_updates.items():
                if col in array_fields:
                    set_clauses.append(f"{col} = %s::text[]")
                elif col in int_fields:
                    set_clauses.append(f"{col} = %s::int")
                else:
                    set_clauses.append(f"{col} = %s")
                values.append(val)
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(set_clauses)}, updated_at = NOW() WHERE id = %s"
            self._execute(query, tuple(values))

        # Ensure preferences row exists, then update
        if preferences_updates:
            self._execute(
                "INSERT INTO user_preferences (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING",
                (user_id,)
            )
            set_clauses = []
            values = []
            for col, val in preferences_updates.items():
                if col in array_fields:
                    set_clauses.append(f"{col} = %s::text[]")
                elif col in int_fields:
                    set_clauses.append(f"{col} = %s::int")
                else:
                    set_clauses.append(f"{col} = %s")
                values.append(val)
            values.append(user_id)
            query = f"UPDATE user_preferences SET {', '.join(set_clauses)}, updated_at = NOW() WHERE user_id = %s"
            self._execute(query, tuple(values))

        # Save signals as flat columns
        if signals_updates:
            self._execute(
                "INSERT INTO user_signals (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING",
                (user_id,)
            )
            set_clauses = ", ".join(f"{col} = %s" for col in signals_updates.keys())
            values = list(signals_updates.values()) + [user_id]
            query = f"UPDATE user_signals SET {set_clauses}, updated_at = NOW() WHERE user_id = %s"
            self._execute(query, tuple(values))

        # Save meta (intent, proxy info) to signals JSONB if present
        if meta and any(v for v in meta.values() if v is not None):
            meta_clean = {k: v for k, v in meta.items() if v is not None}
            self._execute(
                "INSERT INTO user_signals (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING",
                (user_id,)
            )
            # Use the JSONB signals column for meta (not a flat column)
            query = """
                UPDATE user_signals
                SET signals = COALESCE(signals, '{}'::jsonb) || %s::jsonb, updated_at = NOW()
                WHERE user_id = %s
            """
            self._execute(query, (json.dumps({"web_meta": meta_clean}), user_id))

        logger.info(f"Web intake saved: {len(users_updates)} user fields, "
                     f"{len(preferences_updates)} pref fields, "
                     f"{len(signals_updates)} signal fields for user {user_id}")

    # ============== UTILITY ==============

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
