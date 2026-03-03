"""
Postgres adapter for Jodi platform.
Drop-in replacement for existing db.py interface.
Uses psycopg2 and DATABASE_URL env var.
"""
import os
import json
import psycopg2
import psycopg2.extras
from contextlib import contextmanager

DATABASE_URL = os.getenv('DATABASE_URL')


class JodiDB:
    def __init__(self, dsn=None):
        self.dsn = dsn or DATABASE_URL
        if not self.dsn:
            raise RuntimeError('DATABASE_URL environment variable is required')
        self.conn = psycopg2.connect(self.dsn, cursor_factory=psycopg2.extras.RealDictCursor)
        self.conn.autocommit = True
        # ensure users table has conversation_state JSONB column
        try:
            self._ensure_conversation_state_column()
        except Exception:
            # don't fail initialization if migration can't run here
            pass

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

    # ============== USER OPERATIONS ==============
    
    def create_user(self, telegram_id, username=None, first_name=None):
        """Create or get user by telegram_id."""
        sql = """
        INSERT INTO users (telegram_id, email, created_at, last_active)
        VALUES (%s, %s, now(), now())
        ON CONFLICT (telegram_id) DO UPDATE SET last_active = now()
        RETURNING *
        """
        # Use telegram_id as email placeholder if no email
        email = f"{telegram_id}@telegram.jodi"
        return self.fetchone(sql, (telegram_id, email))

    def get_user(self, telegram_id):
        """Get user by telegram_id."""
        return self.fetchone('SELECT * FROM users WHERE telegram_id = %s', (telegram_id,))

    def get_conversation_state(self, telegram_id):
        """Get conversation state for user."""
        user = self.get_user(telegram_id)
        if user:
            # conversation_state is stored as JSONB in users table
            state = user.get('conversation_state')
            if not state:
                return {}
            # If returned as string, parse
            if isinstance(state, str):
                try:
                    return json.loads(state)
                except Exception:
                    return {}
            return state
        return None

    def update_conversation_state(self, telegram_id, state):
        """Update conversation state for user."""
        # Ensure user exists
        user = self.get_user(telegram_id)
        if not user:
            user = self.create_user(telegram_id)
        sql = "UPDATE users SET conversation_state = %s::jsonb, last_active = now() WHERE telegram_id = %s RETURNING *"
        return self.fetchone(sql, (json.dumps(state or {}), telegram_id))

    def _ensure_conversation_state_column(self):
        """Add conversation_state column to users table if missing."""
        col = self.fetchone(
            "SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='conversation_state'"
        )
        if not col:
            # Add the column with default empty jsonb
            self.execute("ALTER TABLE users ADD COLUMN conversation_state JSONB DEFAULT '{}'::jsonb")

    # ============== PROFILE OPERATIONS ==============
    
    def create_or_update_profile(self, telegram_id, profile_dict=None, **kwargs):
        """Create or update profile for a telegram user.
        Accepts either a profile_dict or keyword args from callers.
        """
        # normalize profile_dict
        if profile_dict is None:
            profile_dict = kwargs or {}
        # First get user_id from telegram_id
        user = self.get_user(telegram_id)
        if not user:
            user = self.create_user(telegram_id)
        user_id = user['id']
        
        return self.upsert_profile(user_id, profile_dict)

    def upsert_profile(self, user_id, profile_dict):
        """Insert or update profile by user_id."""
        # Build dynamic update
        allowed_cols = ['display_name', 'dob', 'gender', 'location_text', 'religion', 
                       'relationship_intent', 'smoking', 'drinking', 'wants_children', 
                       'education_level', 'height_cm', 'completeness_score']
        # conversation_history isn't a column in older schemas. Keep it out of upsert to avoid errors.
        json_cols = ['preferences', 'personality_data', 'media_signals', 'conversation_history']
        
        set_parts = []
        vals = []
        
        for c in allowed_cols:
            if c in profile_dict:
                set_parts.append(f"{c} = %s")
                vals.append(profile_dict[c])
        
        for jc in json_cols:
            if jc in profile_dict:
                set_parts.append(f"{jc} = %s::jsonb")
                vals.append(json.dumps(profile_dict[jc]))
        
        if 'embedding' in profile_dict and profile_dict['embedding']:
            set_parts.append("embedding = %s")
            vals.append(profile_dict['embedding'])
        
        if not set_parts:
            return self.get_profile_by_user_id(user_id)
        
        set_sql = ', '.join(set_parts) + ', updated_at = now()'
        
        sql = f"""
        INSERT INTO profiles (user_id, created_at, updated_at)
        VALUES (%s, now(), now())
        ON CONFLICT (user_id) DO UPDATE SET {set_sql}
        RETURNING *
        """
        return self.fetchone(sql, [user_id] + vals)

    def get_profile(self, telegram_id):
        """Get profile by telegram_id. Joins users to include telegram_id in returned dict."""
        sql = "SELECT p.*, u.telegram_id FROM profiles p JOIN users u ON p.user_id = u.id WHERE u.telegram_id = %s"
        row = self.fetchone(sql, (telegram_id,))
        return row

    def get_profile_by_user_id(self, user_id):
        """Get profile by user_id."""
        return self.fetchone('SELECT * FROM profiles WHERE user_id = %s', (user_id,))

    def get_all_profiles(self):
        """Get all profiles."""
        return self.fetchall('SELECT * FROM profiles')

    def mark_profile_complete(self, telegram_id):
        """Mark user's profile as complete."""
        user = self.get_user(telegram_id)
        if not user:
            return None
        self.execute(
            'UPDATE profiles SET completeness_score = 100 WHERE user_id = %s',
            (user['id'],)
        )
        return self.get_profile(telegram_id)

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
            json.dumps(extracted_data or {}),
            interaction_type
        ))

    def get_interactions(self, user_id, limit=100):
        """Get interactions for a user."""
        return self.fetchall(
            'SELECT * FROM interactions WHERE user_id = %s ORDER BY created_at DESC LIMIT %s',
            (user_id, limit)
        )

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
            a_id, b_id, score, json.dumps(score_breakdown or {})
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

    # ============== VECTOR SIMILARITY ==============
    
    def nearest_profiles(self, embedding, limit=10, exclude_user_id=None):
        """Find nearest profiles by embedding similarity."""
        if exclude_user_id:
            sql = """
            SELECT * FROM profiles 
            WHERE embedding IS NOT NULL AND user_id != %s
            ORDER BY embedding <-> %s 
            LIMIT %s
            """
            return self.fetchall(sql, (exclude_user_id, embedding, limit))
        else:
            sql = """
            SELECT * FROM profiles 
            WHERE embedding IS NOT NULL
            ORDER BY embedding <-> %s 
            LIMIT %s
            """
            return self.fetchall(sql, (embedding, limit))

    def raw_query(self, sql, params=None):
        """Execute raw SQL and return results."""
        return self.fetchall(sql, params)


# Test connection when run directly
if __name__ == '__main__':
    db = JodiDB()
    print('Connected to DB')
    rows = db.fetchall("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
    print('Tables:', [r['tablename'] for r in rows])
    db.close()
