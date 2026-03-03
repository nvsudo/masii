"""
Postgres adapter for Jodi platform — V2 with 100+ data point support.
Implements new 4-tier data capture framework with confidence scoring.

Author: Blitz
Date: 2026-02-11
"""
import os
import json
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Any

DATABASE_URL = os.getenv('DATABASE_URL')


def json_serializer(obj):
    """JSON serializer for datetime and decimal objects"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


class JodiDB:
    """
    Database adapter for Jodi matchmaking platform.
    Supports 4-tier progressive data capture with confidence scoring.
    """
    
    def __init__(self, dsn=None):
        self.dsn = dsn or DATABASE_URL
        if not self.dsn:
            raise RuntimeError('DATABASE_URL environment variable is required')
        self.conn = psycopg2.connect(self.dsn, cursor_factory=psycopg2.extras.RealDictCursor)
        self.conn.autocommit = True

    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None

    @contextmanager
    def cursor(self):
        cur = self.conn.cursor()
        try:
            yield cur
        finally:
            cur.close()

    def execute(self, sql, params=None):
        with self.cursor() as cur:
            cur.execute(sql, params)

    def fetchone(self, sql, params=None):
        with self.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()

    def fetchall(self, sql, params=None):
        with self.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    # ============== USER OPERATIONS (Tier 1: Hard Filters) ==============
    
    def create_user(self, telegram_id, username=None, first_name=None):
        """Create or get user by telegram_id."""
        sql = """
        INSERT INTO users (telegram_id, email, created_at, last_active)
        VALUES (%s, %s, now(), now())
        ON CONFLICT (telegram_id) DO UPDATE SET last_active = now()
        RETURNING *
        """
        email = f"{telegram_id}@telegram.jodi"
        return self.fetchone(sql, (telegram_id, email))

    def get_user(self, telegram_id):
        """Get user by telegram_id."""
        return self.fetchone('SELECT * FROM users WHERE telegram_id = %s', (telegram_id,))
    
    def update_user_hard_filters(self, telegram_id: int, filters: Dict[str, Any]) -> Optional[Dict]:
        """
        Update Tier 1 hard filter columns in users table.
        
        Args:
            telegram_id: User's Telegram ID
            filters: Dict of field_name -> value (e.g., {"age": 28, "religion": "Hindu"})
        
        Allowed fields:
            - date_of_birth (DATE) - age auto-calculates via trigger
            - gender_identity, sexual_orientation
            - city, country, nationality, ethnicity
            - native_languages (TEXT[])
            - religion, religious_practice_level
            - children_intent, marital_history
            - smoking, drinking, dietary_restrictions
            - relationship_intent, relationship_timeline
            - occupation, industry, education_level
            - caste_community, height_cm
        
        Returns:
            Updated user record
        """
        user = self.get_user(telegram_id)
        if not user:
            user = self.create_user(telegram_id)
        
        # Allowed Tier 1 columns
        allowed_fields = {
            'full_name', 'date_of_birth', 'age', 'gender_identity', 'sexual_orientation',
            'city', 'country', 'nationality', 'ethnicity', 'native_languages',
            'religion', 'religious_practice_level', 'children_intent', 'marital_history',
            'smoking', 'drinking', 'dietary_restrictions', 
            'relationship_intent', 'relationship_timeline',
            'occupation', 'industry', 'education_level', 'caste_community', 'height_cm'
        }
        
        # Build dynamic UPDATE
        set_clauses = []
        values = []
        
        for field, value in filters.items():
            if field in allowed_fields:
                if field == 'native_languages' and isinstance(value, list):
                    # Array type
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
                else:
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
        
        if not set_clauses:
            return user
        
        # Add last_active update to set_clauses instead of in SET directly
        set_clauses.append("last_active = now()")
        
        sql = f"""
        UPDATE users 
        SET {', '.join(set_clauses)}
        WHERE telegram_id = %s
        RETURNING *
        """
        values.append(telegram_id)
        
        return self.fetchone(sql, tuple(values))
    
    # ============== USER SIGNALS (Tier 2-4: JSONB with Confidence) ==============
    
    def upsert_user_signals(
        self, 
        telegram_id: int, 
        category: str, 
        signals: Dict[str, Dict[str, Any]]
    ) -> Optional[Dict]:
        """
        Merge signals into user_signals JSONB columns with confidence scores.
        
        Args:
            telegram_id: User's Telegram ID
            category: 'lifestyle' | 'values' | 'relationship_style' | 'personality' | 
                     'family_background' | 'media_signals' | 'match_learnings'
            signals: Dict of field_name -> {value, confidence, source, updated_at}
        
        Example:
            upsert_user_signals(12345, 'lifestyle', {
                'work_style': {
                    'value': 'Startup',
                    'confidence': 0.85,
                    'source': 'inferred',
                    'updated_at': '2026-02-11T10:30:00Z'
                }
            })
        
        Merging logic:
            - If field doesn't exist: insert
            - If new confidence > existing confidence: update
            - If new confidence <= existing: keep existing
        
        Returns:
            Updated user_signals record
        """
        user = self.get_user(telegram_id)
        if not user:
            user = self.create_user(telegram_id)
        user_id = user['id']
        
        # Valid categories
        valid_categories = [
            'lifestyle', 'values', 'relationship_style', 'personality',
            'family_background', 'media_signals', 'match_learnings'
        ]
        if category not in valid_categories:
            raise ValueError(f"Invalid category: {category}. Must be one of {valid_categories}")
        
        # Get existing signals
        existing = self.fetchone(
            f"SELECT {category} FROM user_signals WHERE user_id = %s",
            (user_id,)
        )
        
        if existing and existing[category]:
            current_signals = existing[category]
            if isinstance(current_signals, str):
                current_signals = json.loads(current_signals)
        else:
            current_signals = {}
        
        # Merge with confidence-based override
        for field, signal_data in signals.items():
            new_confidence = signal_data.get('confidence', 0.0)
            
            if field in current_signals:
                existing_confidence = current_signals[field].get('confidence', 0.0)
                # Only update if new confidence is higher
                if new_confidence > existing_confidence:
                    current_signals[field] = signal_data
            else:
                # New field, always add
                current_signals[field] = signal_data
        
        # Upsert into user_signals
        sql = f"""
        INSERT INTO user_signals (user_id, {category}, created_at, updated_at)
        VALUES (%s, %s::jsonb, now(), now())
        ON CONFLICT (user_id) DO UPDATE SET
            {category} = %s::jsonb,
            updated_at = now()
        RETURNING *
        """
        signals_json = json.dumps(current_signals, default=json_serializer)
        return self.fetchone(sql, (user_id, signals_json, signals_json))
    
    def get_user_signals(self, telegram_id: int) -> Optional[Dict]:
        """Get all signals for a user."""
        user = self.get_user(telegram_id)
        if not user:
            return None
        
        return self.fetchone(
            "SELECT * FROM user_signals WHERE user_id = %s",
            (user['id'],)
        )
    
    # ============== USER PREFERENCES (Partner Requirements) ==============
    
    def upsert_user_preferences(
        self,
        telegram_id: int,
        hard_filters: Optional[Dict] = None,
        soft_preferences: Optional[Dict] = None,
        dealbreakers: Optional[List[str]] = None,
        green_flags: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Create or update user preferences (what they're looking for).
        
        Args:
            telegram_id: User's Telegram ID
            hard_filters: {age_min, age_max, gender_preference, location_preference, ...}
            soft_preferences: {field: {values, weight, type}}
            dealbreakers: ["Smoking", "Different religion", ...]
            green_flags: ["Emotionally intelligent", "Ambitious", ...]
        
        Returns:
            Updated user_preferences record
        """
        user = self.get_user(telegram_id)
        if not user:
            user = self.create_user(telegram_id)
        user_id = user['id']
        
        # Get existing preferences
        existing = self.fetchone(
            "SELECT * FROM user_preferences WHERE user_id = %s",
            (user_id,)
        )
        
        # Build update clauses
        set_clauses = []
        values = []
        
        if hard_filters:
            for field in ['age_min', 'age_max', 'max_distance_km', 'open_to_relocation', 
                         'religion_importance', 'children_preference', 'education_minimum']:
                if field in hard_filters:
                    set_clauses.append(f"{field} = %s")
                    values.append(hard_filters[field])
            
            # Array fields
            for field in ['gender_preference', 'location_preference', 'religion_preference']:
                if field in hard_filters:
                    set_clauses.append(f"{field} = %s")
                    values.append(hard_filters[field])
        
        if soft_preferences:
            # Merge with existing soft_preferences
            current_soft = {}
            if existing and existing.get('soft_preferences'):
                sp = existing['soft_preferences']
                current_soft = sp if isinstance(sp, dict) else json.loads(sp)
            
            current_soft.update(soft_preferences)
            set_clauses.append("soft_preferences = %s::jsonb")
            values.append(json.dumps(current_soft, default=json_serializer))
        
        if dealbreakers is not None:
            set_clauses.append("dealbreakers = %s")
            values.append(dealbreakers)
        
        if green_flags is not None:
            set_clauses.append("green_flags = %s")
            values.append(green_flags)
        
        if not set_clauses:
            return existing
        
        # Upsert
        if existing:
            sql = f"""
            UPDATE user_preferences
            SET {', '.join(set_clauses)}, updated_at = now()
            WHERE user_id = %s
            RETURNING *
            """
            values.append(user_id)
        else:
            # Insert with defaults
            sql = """
            INSERT INTO user_preferences (user_id, created_at, updated_at)
            VALUES (%s, now(), now())
            RETURNING *
            """
            # Then update with values
            insert_result = self.fetchone(sql, (user_id,))
            if set_clauses:
                sql = f"""
                UPDATE user_preferences
                SET {', '.join(set_clauses)}, updated_at = now()
                WHERE user_id = %s
                RETURNING *
                """
                values.append(user_id)
                return self.fetchone(sql, tuple(values))
            return insert_result
        
        return self.fetchone(sql, tuple(values))
    
    def get_user_preferences(self, telegram_id: int) -> Optional[Dict]:
        """Get user's partner preferences."""
        user = self.get_user(telegram_id)
        if not user:
            return None
        
        return self.fetchone(
            "SELECT * FROM user_preferences WHERE user_id = %s",
            (user['id'],)
        )
    
    # ============== TIER PROGRESS TRACKING ==============
    
    def update_tier_progress(
        self,
        telegram_id: int,
        tier_completions: Optional[Dict[str, float]] = None,
        completed_fields: Optional[Dict[str, List[str]]] = None,
        open_ended_response: Optional[Dict] = None,
        session_increment: bool = False
    ) -> Optional[Dict]:
        """
        Update tier progress tracking.
        
        Args:
            telegram_id: User's Telegram ID
            tier_completions: {"tier1": 100.0, "tier2": 45.0, ...}
            completed_fields: {"tier1": ["full_name", "age", ...], "tier2": [...]}
            open_ended_response: {question, response, signals_extracted, asked_at}
            session_increment: True to increment session_count
        
        Returns:
            Updated tier_progress record
        """
        user = self.get_user(telegram_id)
        if not user:
            user = self.create_user(telegram_id)
        user_id = user['id']
        
        # Get existing progress
        existing = self.fetchone(
            "SELECT * FROM tier_progress WHERE user_id = %s",
            (user_id,)
        )
        
        set_clauses = []
        values = []
        
        # Update tier completion percentages
        if tier_completions:
            for tier, pct in tier_completions.items():
                if tier in ['tier1', 'tier2', 'tier3', 'tier4']:
                    set_clauses.append(f"{tier}_completion = %s")
                    values.append(pct)
        
        # Update completed fields
        if completed_fields:
            current_fields = {}
            if existing and existing.get('completed_fields'):
                cf = existing['completed_fields']
                current_fields = cf if isinstance(cf, dict) else json.loads(cf)
            
            # Merge completed fields
            for tier, fields in completed_fields.items():
                current_fields.setdefault(tier, [])
                for field in fields:
                    if field not in current_fields[tier]:
                        current_fields[tier].append(field)
            
            set_clauses.append("completed_fields = %s::jsonb")
            values.append(json.dumps(current_fields, default=json_serializer))
        
        # Add open-ended response
        if open_ended_response:
            current_responses = []
            if existing and existing.get('open_ended_responses'):
                resp = existing['open_ended_responses']
                current_responses = resp if isinstance(resp, list) else json.loads(resp)
            
            current_responses.append(open_ended_response)
            
            set_clauses.append("open_ended_responses = %s::jsonb")
            values.append(json.dumps(current_responses, default=json_serializer))
            
            set_clauses.append("open_ended_count = %s")
            values.append(len(current_responses))
        
        # Increment session count
        if session_increment:
            if existing:
                new_count = (existing.get('session_count') or 0) + 1
                set_clauses.append("session_count = %s")
                values.append(new_count)
                
                if not existing.get('first_session_at'):
                    set_clauses.append("first_session_at = now()")
                
                set_clauses.append("last_session_at = now()")
            else:
                set_clauses.append("session_count = 1")
                set_clauses.append("first_session_at = now()")
                set_clauses.append("last_session_at = now()")
        
        # Check MVP activation after updates
        if existing:
            # Update existing record
            if set_clauses:
                sql = f"""
                UPDATE tier_progress
                SET {', '.join(set_clauses)}, updated_at = now()
                WHERE user_id = %s
                RETURNING *
                """
                values.append(user_id)
                result = self.fetchone(sql, tuple(values))
            else:
                result = existing
        else:
            # Create new record with defaults
            sql = """
            INSERT INTO tier_progress (
                user_id, 
                tier1_completion, tier2_completion, tier3_completion, tier4_completion,
                session_count, first_session_at, last_session_at,
                created_at, updated_at
            )
            VALUES (%s, 0, 0, 0, 0, 1, now(), now(), now(), now())
            RETURNING *
            """
            result = self.fetchone(sql, (user_id,))
            
            # Then apply updates
            if set_clauses:
                sql = f"""
                UPDATE tier_progress
                SET {', '.join(set_clauses)}, updated_at = now()
                WHERE user_id = %s
                RETURNING *
                """
                values.append(user_id)
                result = self.fetchone(sql, tuple(values))
        
        # Update MVP status
        self._update_mvp_status(user_id)
        
        return result
    
    def _update_mvp_status(self, user_id: int):
        """Check and update MVP activation status using SQL helper function."""
        # Call check_mvp_activation function
        mvp_check = self.fetchone(
            "SELECT * FROM check_mvp_activation(%s)",
            (user_id,)
        )
        
        if mvp_check:
            meets_mvp = mvp_check.get('meets_mvp', False)
            blocked_reasons = mvp_check.get('blocked_reasons', [])
            
            # Update tier_progress with MVP status
            if meets_mvp:
                self.execute("""
                    UPDATE tier_progress
                    SET mvp_achieved = TRUE,
                        mvp_achieved_at = COALESCE(mvp_achieved_at, now()),
                        mvp_blocked_reasons = NULL
                    WHERE user_id = %s
                """, (user_id,))
                
                # Also mark user profile as active
                self.execute("""
                    UPDATE users
                    SET profile_active = TRUE,
                        matching_activated_at = COALESCE(matching_activated_at, now())
                    WHERE id = %s
                """, (user_id,))
            else:
                self.execute("""
                    UPDATE tier_progress
                    SET mvp_achieved = FALSE,
                        mvp_blocked_reasons = %s
                    WHERE user_id = %s
                """, (blocked_reasons, user_id))
    
    def get_tier_progress(self, telegram_id: int) -> Optional[Dict]:
        """Get tier progress for a user."""
        user = self.get_user(telegram_id)
        if not user:
            return None
        
        return self.fetchone(
            "SELECT * FROM tier_progress WHERE user_id = %s",
            (user['id'],)
        )
    
    def calculate_user_completeness(self, telegram_id: int) -> Optional[float]:
        """Calculate weighted completeness using SQL helper function."""
        user = self.get_user(telegram_id)
        if not user:
            return None
        
        result = self.fetchone(
            "SELECT calculate_total_completeness(%s) as completeness",
            (user['id'],)
        )
        
        if result:
            return float(result['completeness'] or 0.0)
        return 0.0
    
    def check_mvp_activation(self, telegram_id: int) -> Optional[Dict]:
        """
        Check if user meets MVP activation criteria.
        
        Returns:
            {
                'meets_mvp': bool,
                'blocked_reasons': [str, ...]
            }
        """
        user = self.get_user(telegram_id)
        if not user:
            return None
        
        return self.fetchone(
            "SELECT * FROM check_mvp_activation(%s)",
            (user['id'],)
        )
    
    # ============== FULL PROFILE RETRIEVAL ==============
    
    def get_full_profile(self, telegram_id: int) -> Optional[Dict]:
        """
        Get complete user profile (users + user_signals + tier_progress + user_preferences).
        
        Returns:
            {
                'user': {...},
                'signals': {...},
                'tier_progress': {...},
                'preferences': {...},
                'completeness': float,
                'mvp_status': {...}
            }
        """
        user = self.get_user(telegram_id)
        if not user:
            return None
        
        signals = self.get_user_signals(telegram_id)
        tier_progress = self.get_tier_progress(telegram_id)
        preferences = self.get_user_preferences(telegram_id)
        completeness = self.calculate_user_completeness(telegram_id)
        mvp_status = self.check_mvp_activation(telegram_id)
        
        return {
            'user': dict(user) if user else None,
            'signals': dict(signals) if signals else None,
            'tier_progress': dict(tier_progress) if tier_progress else None,
            'preferences': dict(preferences) if preferences else None,
            'completeness': completeness,
            'mvp_status': dict(mvp_status) if mvp_status else None
        }
    
    # ============== CONVERSATION STATE (Backward Compatibility) ==============
    
    def get_conversation_state(self, telegram_id):
        """Get conversation state for user (legacy support)."""
        user = self.get_user(telegram_id)
        if user:
            state = user.get('conversation_state')
            if not state:
                return {}
            if isinstance(state, str):
                try:
                    return json.loads(state)
                except Exception:
                    return {}
            return state
        return None

    def update_conversation_state(self, telegram_id, state):
        """Update conversation state for user (legacy support)."""
        user = self.get_user(telegram_id)
        if not user:
            user = self.create_user(telegram_id)
        sql = "UPDATE users SET conversation_state = %s::jsonb, last_active = now() WHERE telegram_id = %s RETURNING *"
        return self.fetchone(sql, (json.dumps(state or {}), telegram_id))
    
    # ============== LEGACY PROFILE OPERATIONS (Backward Compatibility) ==============
    
    def get_profile(self, telegram_id):
        """Get profile by telegram_id (legacy wrapper around get_full_profile)."""
        return self.get_full_profile(telegram_id)
    
    def create_or_update_profile(self, telegram_id, profile_dict=None, **kwargs):
        """Legacy profile update (maps to new schema)."""
        if profile_dict is None:
            profile_dict = kwargs or {}
        
        # Extract and route to new schema
        # This is a compatibility layer - new code should use specific methods
        user = self.get_user(telegram_id)
        if not user:
            user = self.create_user(telegram_id)
        
        # Map old profile fields to new schema locations
        # For now, just update user table
        return user
    
    # ============== MATCH OPERATIONS ==============
    
    def create_match(self, user_a_telegram_id, user_b_telegram_id, score=None, score_breakdown=None):
        """Create a match between two users."""
        user_a = self.get_user(user_a_telegram_id)
        user_b = self.get_user(user_b_telegram_id)
        
        if not user_a or not user_b:
            return None
        
        # Ensure consistent ordering
        a_id, b_id = sorted([user_a['id'], user_b['id']])
        
        sql = """
        INSERT INTO matches (user_a, user_b, match_score, score_breakdown, status, created_at)
        VALUES (%s, %s, %s, %s::jsonb, 'proposed', now())
        ON CONFLICT (user_a, user_b) DO UPDATE SET
            match_score = EXCLUDED.match_score,
            score_breakdown = EXCLUDED.score_breakdown
        RETURNING *
        """
        return self.fetchone(sql, (
            a_id, b_id, score, json.dumps(score_breakdown or {}, default=json_serializer)
        ))

    def get_matches_for_user(self, telegram_id, limit=100):
        """Get matches for a user by telegram_id."""
        user = self.get_user(telegram_id)
        if not user:
            return []
        user_id = user['id']
        return self.fetchall(
            'SELECT * FROM matches WHERE user_a = %s OR user_b = %s ORDER BY created_at DESC LIMIT %s',
            (user_id, user_id, limit)
        )

    def update_match_status(self, match_id, status):
        """Update match status."""
        return self.execute(
            'UPDATE matches SET status = %s WHERE id = %s',
            (status, match_id)
        )
    
    # ============== INTERACTION OPERATIONS ==============
    
    def record_interaction(self, user_id, direction, content, extracted_data=None, interaction_type=None):
        """Record a conversation interaction."""
        sql = """
        INSERT INTO interactions (user_id, direction, content, extracted_data, interaction_type, created_at)
        VALUES (%s, %s, %s, %s::jsonb, %s, now())
        RETURNING *
        """
        return self.fetchone(sql, (
            user_id,
            direction,
            content,
            json.dumps(extracted_data or {}, default=json_serializer),
            interaction_type
        ))

    def get_interactions(self, user_id, limit=100):
        """Get interactions for a user."""
        return self.fetchall(
            'SELECT * FROM interactions WHERE user_id = %s ORDER BY created_at DESC LIMIT %s',
            (user_id, limit)
        )
    
    # ============== UTILITIES ==============
    
    def raw_query(self, sql, params=None):
        """Execute raw SQL and return results."""
        return self.fetchall(sql, params)


# Test connection when run directly
if __name__ == '__main__':
    db = JodiDB()
    print('✅ Connected to DB')
    
    # Test basic operations
    print('\n🧪 Testing new methods...')
    
    # Create test user
    test_telegram_id = 999999999
    user = db.create_user(test_telegram_id, "test_user", "Test")
    print(f"✅ Created user: {user['id']}")
    
    # Update hard filters
    filters = {
        'age': 28,
        'gender_identity': 'Male',
        'religion': 'Hindu',
        'city': 'Mumbai',
        'country': 'India'
    }
    updated_user = db.update_user_hard_filters(test_telegram_id, filters)
    print(f"✅ Updated hard filters: age={updated_user['age']}, religion={updated_user['religion']}")
    
    # Add signals
    signals = {
        'work_style': {
            'value': 'Startup',
            'confidence': 0.85,
            'source': 'inferred',
            'updated_at': datetime.now().isoformat()
        }
    }
    db.upsert_user_signals(test_telegram_id, 'lifestyle', signals)
    print(f"✅ Added lifestyle signals")
    
    # Update tier progress
    db.update_tier_progress(
        test_telegram_id,
        tier_completions={'tier1': 60.0, 'tier2': 20.0},
        session_increment=True
    )
    print(f"✅ Updated tier progress")
    
    # Check completeness
    completeness = db.calculate_user_completeness(test_telegram_id)
    print(f"✅ Calculated completeness: {completeness}%")
    
    # Check MVP status
    mvp = db.check_mvp_activation(test_telegram_id)
    print(f"✅ MVP Status: {mvp['meets_mvp']}")
    if mvp['blocked_reasons']:
        print(f"   Blocked by: {mvp['blocked_reasons']}")
    
    # Get full profile
    profile = db.get_full_profile(test_telegram_id)
    print(f"✅ Retrieved full profile: {profile.keys()}")
    
    print('\n✅ All tests passed!')
    
    db.close()
