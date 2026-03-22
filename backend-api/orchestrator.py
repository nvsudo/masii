"""
Masii Orchestrator - Process form_submissions into users/preferences/signals tables
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import argparse
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres.herqdldjaxmfusjjpwdg:syO9opxb37SlEV9Q@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"


def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def extract_field_value(answer_data: Dict[str, Any]) -> Any:
    """Extract value from answer data (handles different formats)."""
    if isinstance(answer_data, dict) and 'value' in answer_data:
        return answer_data['value']
    return answer_data


def group_answers_by_table(answers: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Group answer fields by target table.
    Returns: {
        'users': { field: value, ... },
        'preferences': { field: value, ... },
        'signals': { field: value, ... }
    }
    """
    grouped = {
        'users': {},
        'preferences': {},
        'signals': {}
    }
    
    for field, answer_data in answers.items():
        # Extract table and value
        table = answer_data.get('table', 'users') if isinstance(answer_data, dict) else 'users'
        value = extract_field_value(answer_data)
        
        # Map to target table
        if table == 'meta':
            # Skip meta fields
            continue
        elif table in grouped:
            grouped[table][field] = value
        else:
            logger.warning(f"Unknown table '{table}' for field '{field}', defaulting to users")
            grouped['users'][field] = value
    
    return grouped


def upsert_user(cursor, user_data: Dict[str, Any], email: Optional[str], phone: Optional[str]) -> Optional[str]:
    """
    Insert or update user record.
    Returns user_id (UUID).
    """
    # Extract identity fields
    full_name = user_data.get('full_name')
    preferred_name = user_data.get('preferred_name')
    
    # Check if user exists
    if email:
        cursor.execute("""
            SELECT id FROM users WHERE email = %s LIMIT 1
        """, (email,))
    elif phone:
        cursor.execute("""
            SELECT id FROM users WHERE phone = %s LIMIT 1
        """, (phone,))
    else:
        logger.error("No email or phone to identify user")
        return None
    
    existing = cursor.fetchone()
    
    if existing:
        user_id = existing['id']
        # Update user
        set_clause = ', '.join([f"{k} = %s" for k in user_data.keys()])
        values = list(user_data.values()) + [user_id]
        cursor.execute(f"""
            UPDATE users SET {set_clause} WHERE id = %s
        """, values)
        logger.info(f"Updated user {user_id}")
    else:
        # Insert new user
        # Add email and phone
        user_data['email'] = email
        user_data['phone'] = phone
        
        fields = ', '.join(user_data.keys())
        placeholders = ', '.join(['%s'] * len(user_data))
        cursor.execute(f"""
            INSERT INTO users ({fields}) VALUES ({placeholders})
            RETURNING id
        """, list(user_data.values()))
        
        result = cursor.fetchone()
        user_id = result['id']
        logger.info(f"Created user {user_id}")
    
    return user_id


def upsert_preferences(cursor, user_id: str, pref_data: Dict[str, Any]):
    """Insert or update user_preferences."""
    if not pref_data:
        return
    
    # Check if preferences exist
    cursor.execute("""
        SELECT id FROM user_preferences WHERE user_id = %s LIMIT 1
    """, (user_id,))
    
    existing = cursor.fetchone()
    
    if existing:
        # Update
        set_clause = ', '.join([f"{k} = %s" for k in pref_data.keys()])
        values = list(pref_data.values()) + [user_id]
        cursor.execute(f"""
            UPDATE user_preferences SET {set_clause} WHERE user_id = %s
        """, values)
        logger.info(f"Updated preferences for user {user_id}")
    else:
        # Insert
        pref_data['user_id'] = user_id
        fields = ', '.join(pref_data.keys())
        placeholders = ', '.join(['%s'] * len(pref_data))
        cursor.execute(f"""
            INSERT INTO user_preferences ({fields}) VALUES ({placeholders})
        """, list(pref_data.values()))
        logger.info(f"Created preferences for user {user_id}")


def upsert_signals(cursor, user_id: str, signals_data: Dict[str, Any]):
    """Insert or update user_signals."""
    if not signals_data:
        return
    
    # Check if signals exist
    cursor.execute("""
        SELECT id FROM user_signals WHERE user_id = %s LIMIT 1
    """, (user_id,))
    
    existing = cursor.fetchone()
    
    if existing:
        # Update
        set_clause = ', '.join([f"{k} = %s" for k in signals_data.keys()])
        values = list(signals_data.values()) + [user_id]
        cursor.execute(f"""
            UPDATE user_signals SET {set_clause} WHERE user_id = %s
        """, values)
        logger.info(f"Updated signals for user {user_id}")
    else:
        # Insert
        signals_data['user_id'] = user_id
        fields = ', '.join(signals_data.keys())
        placeholders = ', '.join(['%s'] * len(signals_data))
        cursor.execute(f"""
            INSERT INTO user_signals ({fields}) VALUES ({placeholders})
        """, list(signals_data.values()))
        logger.info(f"Created signals for user {user_id}")


def process_submission(cursor, submission: Dict[str, Any], dry_run: bool = False):
    """Process a single form submission."""
    submission_id = submission['id']
    submission_data = submission['submission_data']
    
    logger.info(f"Processing submission {submission_id}")
    
    # Extract data
    phone = submission_data.get('phone')
    email = submission_data.get('meta', {}).get('email')
    answers = submission_data.get('answers', {})
    
    # Group answers by table
    grouped = group_answers_by_table(answers)
    
    logger.info(f"  Users fields: {len(grouped['users'])}")
    logger.info(f"  Preferences fields: {len(grouped['preferences'])}")
    logger.info(f"  Signals fields: {len(grouped['signals'])}")
    
    if dry_run:
        logger.info(f"  [DRY RUN] Would process submission {submission_id}")
        return
    
    # Upsert into tables
    user_id = upsert_user(cursor, grouped['users'], email, phone)
    
    if user_id:
        upsert_preferences(cursor, user_id, grouped['preferences'])
        upsert_signals(cursor, user_id, grouped['signals'])
        
        # Mark submission as processed
        cursor.execute("""
            UPDATE form_submissions 
            SET status = 'processed', processed = TRUE 
            WHERE id = %s
        """, (submission_id,))
        
        logger.info(f"✅ Processed submission {submission_id} for user {user_id}")
    else:
        logger.error(f"❌ Failed to process submission {submission_id}: no user_id")


def main():
    parser = argparse.ArgumentParser(description='Masii Orchestrator - Process form submissions')
    parser.add_argument('--dry-run', action='store_true', help='Log what would happen without making changes')
    parser.add_argument('--id', type=int, help='Process specific submission ID')
    
    args = parser.parse_args()
    
    logger.info("Masii Orchestrator starting...")
    
    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No changes will be made")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("BEGIN")
            
            # Fetch submissions to process
            if args.id:
                cursor.execute("""
                    SELECT * FROM form_submissions
                    WHERE id = %s AND status = 'submitted' AND processed = FALSE
                """, (args.id,))
            else:
                cursor.execute("""
                    SELECT * FROM form_submissions
                    WHERE status = 'submitted' AND processed = FALSE
                    ORDER BY created_at ASC
                """)
            
            submissions = cursor.fetchall()
            
            logger.info(f"Found {len(submissions)} submissions to process")
            
            if len(submissions) == 0:
                logger.info("✨ No submissions to process")
                cursor.execute("ROLLBACK")
                return
            
            # Process each submission
            for submission in submissions:
                try:
                    process_submission(cursor, submission, dry_run=args.dry_run)
                except Exception as e:
                    logger.error(f"Error processing submission {submission['id']}: {e}")
                    # Continue with next submission
                    continue
            
            if args.dry_run:
                cursor.execute("ROLLBACK")
                logger.info("🔍 DRY RUN COMPLETE - No changes committed")
            else:
                cursor.execute("COMMIT")
                logger.info(f"✅ Processed {len(submissions)} submissions successfully")
        
        except Exception as e:
            cursor.execute("ROLLBACK")
            logger.error(f"Transaction error: {e}")
            raise
        
        finally:
            cursor.close()
            conn.close()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
