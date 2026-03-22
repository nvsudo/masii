"""
Masii Bot API - Form Intake Endpoint
Receives form submissions from masii.co and stores them in Supabase.
Uses a staging table approach to avoid schema mismatches.
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

app = FastAPI(title="Masii Bot API", version="1.0.0")

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
    answers: Dict[str, AnswerValue] = Field(default_factory=dict)
    meta: IntakeMeta = Field(default_factory=IntakeMeta)
    type: Optional[str] = None
    proxy_data: Optional[Dict[str, Any]] = None


def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")


def ensure_staging_table(cursor):
    """Create form_submissions staging table if it doesn't exist."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS form_submissions (
            id SERIAL PRIMARY KEY,
            phone TEXT,
            email TEXT,
            full_name TEXT,
            preferred_name TEXT,
            submission_data JSONB,
            intent TEXT,
            processed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_form_submissions_phone ON form_submissions(phone)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_form_submissions_email ON form_submissions(email)
    """)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "masii-bot", "version": "1.0.0"}


@app.post("/api/intake")
async def intake_form(payload: IntakePayload, request: Request):
    """
    Handle form submissions from masii.co.
    Stores in staging table for processing by Masii orchestrator.
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
            
            # Ensure staging table exists
            ensure_staging_table(cursor)
            
            if payload.type == "proxy":
                # Store proxy submission
                cursor.execute("""
                    INSERT INTO form_submissions (
                        phone, email, full_name, submission_data, intent, processed
                    )
                    VALUES (
                        %(phone)s, %(email)s, %(name)s, %(data)s, 'proxy', FALSE
                    )
                    RETURNING id
                """, {
                    "phone": payload.proxy_data.get("person_phone") if payload.proxy_data else None,
                    "email": payload.meta.email,
                    "name": payload.proxy_data.get("person_name") if payload.proxy_data else None,
                    "data": json.dumps(payload.model_dump())
                })
                result = cursor.fetchone()
                submission_id = result["id"]
                
                cursor.execute("COMMIT")
                logger.info(f"Stored proxy submission: {submission_id}")
                
                return {
                    "success": True,
                    "submission_id": submission_id,
                    "mode": "proxy",
                    "message": "Proxy submission received"
                }
            
            # Normal self-submission
            # Check if submission exists
            check_query = """
                SELECT id FROM form_submissions
                WHERE phone = %(phone)s OR (email = %(email)s AND email IS NOT NULL)
                ORDER BY created_at DESC
                LIMIT 1
            """
            cursor.execute(check_query, {
                "phone": payload.phone,
                "email": payload.meta.email
            })
            existing = cursor.fetchone()
            
            if existing:
                # Update existing submission
                update_query = """
                    UPDATE form_submissions
                    SET 
                        full_name = COALESCE(%(name)s, full_name),
                        preferred_name = COALESCE(%(preferred_name)s, preferred_name),
                        email = COALESCE(%(email)s, email),
                        submission_data = %(data)s,
                        intent = %(intent)s,
                        processed = FALSE,
                        updated_at = NOW()
                    WHERE id = %(id)s
                    RETURNING id
                """
                cursor.execute(update_query, {
                    "id": existing["id"],
                    "name": payload.name,
                    "preferred_name": payload.preferred_name,
                    "email": payload.meta.email,
                    "data": json.dumps(payload.model_dump()),
                    "intent": payload.meta.intent or "self"
                })
                submission_id = existing["id"]
                logger.info(f"Updated submission: {submission_id}")
            else:
                # Insert new submission
                insert_query = """
                    INSERT INTO form_submissions (
                        phone, email, full_name, preferred_name,
                        submission_data, intent, processed
                    )
                    VALUES (
                        %(phone)s, %(email)s, %(name)s, %(preferred_name)s,
                        %(data)s, %(intent)s, FALSE
                    )
                    RETURNING id
                """
                cursor.execute(insert_query, {
                    "phone": payload.phone,
                    "email": payload.meta.email,
                    "name": payload.name,
                    "preferred_name": payload.preferred_name,
                    "data": json.dumps(payload.model_dump()),
                    "intent": payload.meta.intent or "self"
                })
                result = cursor.fetchone()
                submission_id = result["id"]
                logger.info(f"Created new submission: {submission_id}")
            
            cursor.execute("COMMIT")
            
            return {
                "success": True,
                "submission_id": submission_id,
                "message": "Form submitted successfully. Masii will process it shortly."
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
