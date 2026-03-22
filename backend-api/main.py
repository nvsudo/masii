"""
Masii Bot API - Form Intake with Inline Processing
Receives form submissions from masii.co, stores in staging table,
and immediately processes to final tables (users/preferences/signals).
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Masii Bot API", version="1.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection string
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.herqdldjaxmfusjjpwdg:syO9opxb37SlEV9Q@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"
)


# ============================================
# MODELS
# ============================================

class AnswerValue(BaseModel):
    value: Any
    table: str


class IntakeMeta(BaseModel):
    intent: Optional[str] = None
    email: Optional[str] = None
    proxy: Optional[Dict[str, Any]] = Field(default_factory=dict)


class IntakePayload(BaseModel):
    phone: Optional[str] = None
    name: Optional[str] = None
    preferred_name: Optional[str] = None
    answers: Dict[str, Any] = Field(default_factory=dict)
    meta: IntakeMeta = Field(default_factory=IntakeMeta)
    type: Optional[str] = None
    proxy_data: Optional[Dict[str, Any]] = None


class DraftPayload(BaseModel):
    user_id: str
    submission_data: Dict[str, Any]
    current_question: Optional[str] = None


# ============================================
# DATABASE HELPERS
# ============================================

def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")


def ensure_tables(cursor):
    """Create staging table if it doesn't exist."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS form_submissions (
            id SERIAL PRIMARY KEY,
            user_id UUID,
            phone TEXT,
            email TEXT,
            full_name TEXT,
            preferred_name TEXT,
            submission_data JSONB,
            current_question TEXT,
            status TEXT DEFAULT 'submitted',
            intent TEXT,
            processed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_form_submissions_phone ON form_submissions(phone)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_form_submissions_email ON form_submissions(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_form_submissions_user_id ON form_submissions(user_id)")


# ============================================
# INLINE ORCHESTRATOR (Option C)
# ============================================

def extract_field_value(answer_data: Any) -> Any:
    """Extract value from answer data."""
    if isinstance(answer_data, dict) and 'value' in answer_data:
        return answer_data['value']
    return answer_data


def get_table_for_field(answer_data: Any) -> str:
    """Get target table from answer data."""
    if isinstance(answer_data, dict) and 'table' in answer_data:
        return answer_data['table']
    return 'users'


def group_answers_by_table(answers: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Group answer fields by target table."""
    grouped = {'users': {}, 'preferences': {}, 'signals': {}}
    
    for field, answer_data in answers.items():
        table = get_table_for_field(answer_data)
        value = extract_field_value(answer_data)
        
        if table == 'meta':
            continue
        elif table in grouped:
            grouped[table][field] = value
        else:
            grouped['users'][field] = value
    
    return grouped


def safe_column_name(field: str) -> str:
    """Sanitize column name to prevent SQL injection."""
    # Only allow alphanumeric and underscore
    return ''.join(c for c in field if c.isalnum() or c == '_')


def upsert_user(cursor, user_data: Dict[str, Any], email: Optional[str], phone: Optional[str]) -> Optional[str]:
    """Insert or update user record. Returns user_id."""
    if not email:
        logger.error("No email to identify user (phone not stored in users table)")
        return None
    
    # Check if user exists (by email only - users table has no phone column)
    cursor.execute("SELECT id FROM users WHERE email = %s LIMIT 1", (email,))
    
    existing = cursor.fetchone()
    
    # Filter to only valid columns (must match actual DB schema)
    # From Supabase OpenAPI: users table columns
    valid_user_fields = [
        'full_name', 'gender', 'date_of_birth', 'age', 'religion',
        'mother_tongue', 'city_current', 'state_india', 'country_current',
        'marital_status', 'children_existing', 'height_cm', 'weight_kg',
        'education_level', 'education_field', 'occupation_sector',
        'annual_income', 'family_type', 'family_status',
        'father_occupation', 'mother_occupation', 'siblings',
        'hometown_city', 'hometown_state', 'languages_spoken',
        'known_conditions', 'email'
        # Note: phone is used for lookup, not stored directly
    ]
    
    filtered_data = {k: v for k, v in user_data.items() if k in valid_user_fields}
    
    if existing:
        user_id = existing['id']
        if filtered_data:
            set_clause = ', '.join([f"{safe_column_name(k)} = %s" for k in filtered_data.keys()])
            values = list(filtered_data.values()) + [user_id]
            cursor.execute(f"UPDATE users SET {set_clause}, updated_at = NOW() WHERE id = %s", values)
        logger.info(f"Updated user {user_id}")
        return str(user_id)
    else:
        # Add email (phone not stored in users table)
        filtered_data['email'] = email
        
        if not filtered_data:
            return None
            
        fields = ', '.join([safe_column_name(k) for k in filtered_data.keys()])
        placeholders = ', '.join(['%s'] * len(filtered_data))
        cursor.execute(
            f"INSERT INTO users ({fields}) VALUES ({placeholders}) RETURNING id",
            list(filtered_data.values())
        )
        result = cursor.fetchone()
        user_id = result['id']
        logger.info(f"Created user {user_id}")
        return str(user_id)


def upsert_preferences(cursor, user_id: str, pref_data: Dict[str, Any]):
    """Insert or update user_preferences."""
    if not pref_data:
        return
    
    cursor.execute("SELECT id FROM user_preferences WHERE user_id = %s LIMIT 1", (user_id,))
    existing = cursor.fetchone()
    
    # Filter to valid preference columns (from Supabase OpenAPI)
    valid_pref_fields = [
        'pref_age_min', 'pref_age_max', 'pref_height_min', 'pref_height_max',
        'pref_religion', 'pref_religion_exclude', 'pref_caste', 'pref_caste_exclude',
        'pref_mother_tongue', 'pref_education_min', 'pref_income_min',
        'pref_diet', 'pref_smoking', 'pref_drinking', 'pref_conditions',
        'pref_manglik', 'pref_gotra_exclude', 'pref_family_status',
        'pref_partner_cooking', 'pref_partner_household',
        'caste_importance', 'partner_working', 'religious_practice',
        'sect_denomination', 'caste_community',
        'marriage_timeline', 'children_intent', 'children_timeline',
        'living_arrangement', 'relocation_willingness', 'family_involvement'
    ]
    
    filtered_data = {k: v for k, v in pref_data.items() if k in valid_pref_fields}
    
    if not filtered_data:
        return
    
    if existing:
        set_clause = ', '.join([f"{safe_column_name(k)} = %s" for k in filtered_data.keys()])
        values = list(filtered_data.values()) + [user_id]
        cursor.execute(f"UPDATE user_preferences SET {set_clause} WHERE user_id = %s", values)
        logger.info(f"Updated preferences for user {user_id}")
    else:
        filtered_data['user_id'] = user_id
        fields = ', '.join([safe_column_name(k) for k in filtered_data.keys()])
        placeholders = ', '.join(['%s'] * len(filtered_data))
        cursor.execute(
            f"INSERT INTO user_preferences ({fields}) VALUES ({placeholders})",
            list(filtered_data.values())
        )
        logger.info(f"Created preferences for user {user_id}")


def upsert_signals(cursor, user_id: str, signals_data: Dict[str, Any]):
    """Insert or update user_signals."""
    if not signals_data:
        return
    
    cursor.execute("SELECT id FROM user_signals WHERE user_id = %s LIMIT 1", (user_id,))
    existing = cursor.fetchone()
    
    # Filter to valid signal columns (from Supabase OpenAPI)
    valid_signal_fields = [
        'diet', 'smoking', 'drinking', 'fitness_frequency',
        'social_style', 'conflict_style', 'family_values',
        'manglik_status', 'gotra', 'family_property',
        'financial_planning', 'cooking_contribution', 'household_contribution',
        'do_you_cook', 'career_after_marriage', 'financial_contribution',
        'live_with_inlaws',
        # JSONB blobs (can store complex data):
        'lifestyle', 'values', 'relationship_style', 'personality',
        'family_background', 'media_signals', 'match_learnings'
    ]
    
    filtered_data = {k: v for k, v in signals_data.items() if k in valid_signal_fields}
    
    if not filtered_data:
        return
    
    if existing:
        set_clause = ', '.join([f"{safe_column_name(k)} = %s" for k in filtered_data.keys()])
        values = list(filtered_data.values()) + [user_id]
        cursor.execute(f"UPDATE user_signals SET {set_clause} WHERE user_id = %s", values)
        logger.info(f"Updated signals for user {user_id}")
    else:
        filtered_data['user_id'] = user_id
        fields = ', '.join([safe_column_name(k) for k in filtered_data.keys()])
        placeholders = ', '.join(['%s'] * len(filtered_data))
        cursor.execute(
            f"INSERT INTO user_signals ({fields}) VALUES ({placeholders})",
            list(filtered_data.values())
        )
        logger.info(f"Created signals for user {user_id}")


def process_to_final_tables(cursor, submission_id: int, submission_data: Dict[str, Any], email: str, phone: str) -> bool:
    """
    Process submission data into final tables (users, preferences, signals).
    Returns True on success, False on failure.
    """
    try:
        answers = submission_data.get('answers', {})
        if not answers:
            logger.warning(f"No answers in submission {submission_id}")
            return False
        
        # Group by target table
        grouped = group_answers_by_table(answers)
        
        # Add name fields to users
        if submission_data.get('name'):
            grouped['users']['full_name'] = submission_data['name']
        if submission_data.get('preferred_name'):
            grouped['users']['preferred_name'] = submission_data['preferred_name']
        
        logger.info(f"Processing submission {submission_id}: users={len(grouped['users'])}, prefs={len(grouped['preferences'])}, signals={len(grouped['signals'])}")
        
        # Upsert into final tables
        user_id = upsert_user(cursor, grouped['users'], email, phone)
        
        if not user_id:
            logger.error(f"Failed to create/update user for submission {submission_id}")
            return False
        
        upsert_preferences(cursor, user_id, grouped['preferences'])
        
        # Signals insertion may fail due to DB trigger - use savepoint to not block
        try:
            cursor.execute("SAVEPOINT signals_savepoint")
            upsert_signals(cursor, user_id, grouped['signals'])
            cursor.execute("RELEASE SAVEPOINT signals_savepoint")
        except Exception as sig_err:
            cursor.execute("ROLLBACK TO SAVEPOINT signals_savepoint")
            logger.warning(f"Signals insertion failed (non-blocking): {sig_err}")
        
        # Mark submission as processed
        cursor.execute("""
            UPDATE form_submissions 
            SET status = 'processed', processed = TRUE, updated_at = NOW()
            WHERE id = %s
        """, (submission_id,))
        
        logger.info(f"✅ Processed submission {submission_id} → user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing submission {submission_id}: {e}")
        return False


# ============================================
# ENDPOINTS
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "masii-bot", "version": "1.1.0"}


@app.post("/api/intake")
async def intake_form(payload: IntakePayload, request: Request):
    """
    Handle form submissions from masii.co.
    1. Stores in staging table (form_submissions)
    2. Immediately processes to final tables (users/preferences/signals)
    """
    try:
        logger.info(f"Received intake from {request.client.host}")
        
        # Validate required fields
        if payload.type != "proxy" and not payload.phone:
            raise HTTPException(status_code=400, detail="Missing required field: phone")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("BEGIN")
            ensure_tables(cursor)
            
            email = payload.meta.email
            phone = payload.phone
            submission_data = payload.model_dump()
            
            if payload.type == "proxy":
                # Proxy submissions: store only, don't process yet
                cursor.execute("""
                    INSERT INTO form_submissions (
                        phone, email, full_name, submission_data, intent, status, processed
                    ) VALUES (
                        %(phone)s, %(email)s, %(name)s, %(data)s, 'proxy', 'submitted', FALSE
                    ) RETURNING id
                """, {
                    "phone": payload.proxy_data.get("person_phone") if payload.proxy_data else None,
                    "email": email,
                    "name": payload.proxy_data.get("person_name") if payload.proxy_data else None,
                    "data": json.dumps(submission_data)
                })
                result = cursor.fetchone()
                submission_id = result["id"]
                cursor.execute("COMMIT")
                
                return {
                    "success": True,
                    "submission_id": submission_id,
                    "mode": "proxy",
                    "message": "Proxy submission received. We'll reach out to them."
                }
            
            # Self-submission: check for existing
            cursor.execute("""
                SELECT id FROM form_submissions
                WHERE phone = %(phone)s OR (email = %(email)s AND email IS NOT NULL)
                ORDER BY created_at DESC LIMIT 1
            """, {"phone": phone, "email": email})
            existing = cursor.fetchone()
            
            if existing:
                # Update existing
                cursor.execute("""
                    UPDATE form_submissions SET
                        full_name = COALESCE(%(name)s, full_name),
                        preferred_name = COALESCE(%(preferred_name)s, preferred_name),
                        email = COALESCE(%(email)s, email),
                        submission_data = %(data)s,
                        intent = %(intent)s,
                        status = 'submitted',
                        processed = FALSE,
                        updated_at = NOW()
                    WHERE id = %(id)s
                    RETURNING id
                """, {
                    "id": existing["id"],
                    "name": payload.name,
                    "preferred_name": payload.preferred_name,
                    "email": email,
                    "data": json.dumps(submission_data),
                    "intent": payload.meta.intent or "self"
                })
                submission_id = existing["id"]
                logger.info(f"Updated submission: {submission_id}")
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO form_submissions (
                        phone, email, full_name, preferred_name,
                        submission_data, intent, status, processed
                    ) VALUES (
                        %(phone)s, %(email)s, %(name)s, %(preferred_name)s,
                        %(data)s, %(intent)s, 'submitted', FALSE
                    ) RETURNING id
                """, {
                    "phone": phone,
                    "email": email,
                    "name": payload.name,
                    "preferred_name": payload.preferred_name,
                    "data": json.dumps(submission_data),
                    "intent": payload.meta.intent or "self"
                })
                result = cursor.fetchone()
                submission_id = result["id"]
                logger.info(f"Created submission: {submission_id}")
            
            # === INLINE PROCESSING (Option C) ===
            processed = process_to_final_tables(cursor, submission_id, submission_data, email, phone)
            
            cursor.execute("COMMIT")
            
            if processed:
                return {
                    "success": True,
                    "submission_id": submission_id,
                    "processed": True,
                    "message": "You're in! Masii is already looking for your person."
                }
            else:
                return {
                    "success": True,
                    "submission_id": submission_id,
                    "processed": False,
                    "message": "Form submitted. Masii will process it shortly."
                }
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        finally:
            cursor.close()
            conn.close()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/draft")
async def get_draft(user_id: str):
    """Get draft submission for a user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT status, current_question, submission_data
                FROM form_submissions
                WHERE user_id = %s
                ORDER BY created_at DESC LIMIT 1
            """, (user_id,))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="No draft found")
            
            return {
                "status": result["status"],
                "current_question": result["current_question"],
                "submission_data": result["submission_data"]
            }
        finally:
            cursor.close()
            conn.close()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching draft: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/draft")
async def upsert_draft(payload: DraftPayload):
    """Upsert draft row (auto-save progress)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("BEGIN")
            
            cursor.execute("""
                SELECT id FROM form_submissions
                WHERE user_id = %s ORDER BY created_at DESC LIMIT 1
            """, (payload.user_id,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                    UPDATE form_submissions SET
                        submission_data = %s,
                        current_question = %s,
                        status = 'draft',
                        updated_at = NOW()
                    WHERE id = %s
                """, (json.dumps(payload.submission_data), payload.current_question, existing["id"]))
            else:
                cursor.execute("""
                    INSERT INTO form_submissions (user_id, submission_data, current_question, status, processed)
                    VALUES (%s, %s, %s, 'draft', FALSE)
                """, (payload.user_id, json.dumps(payload.submission_data), payload.current_question))
            
            cursor.execute("COMMIT")
            return {"success": True, "message": "Draft saved"}
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            raise e
        finally:
            cursor.close()
            conn.close()
    
    except Exception as e:
        logger.error(f"Error upserting draft: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/intake/{submission_id}")
async def update_submission(submission_id: int, payload: IntakePayload):
    """Update existing submission (edit mode) and reprocess."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("BEGIN")
            
            submission_data = payload.model_dump()
            email = payload.meta.email
            phone = payload.phone
            
            cursor.execute("""
                UPDATE form_submissions SET
                    full_name = COALESCE(%s, full_name),
                    preferred_name = COALESCE(%s, preferred_name),
                    email = COALESCE(%s, email),
                    phone = COALESCE(%s, phone),
                    submission_data = %s,
                    status = 'submitted',
                    processed = FALSE,
                    updated_at = NOW()
                WHERE id = %s
                RETURNING id
            """, (payload.name, payload.preferred_name, email, phone, json.dumps(submission_data), submission_id))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Submission not found")
            
            # Reprocess to final tables
            processed = process_to_final_tables(cursor, submission_id, submission_data, email, phone)
            
            cursor.execute("COMMIT")
            
            return {
                "success": True,
                "submission_id": submission_id,
                "processed": processed,
                "message": "Profile updated!" if processed else "Update saved, processing shortly."
            }
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            raise e
        finally:
            cursor.close()
            conn.close()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating submission: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
