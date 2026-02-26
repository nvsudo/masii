#!/usr/bin/env python3
"""
Apply schema migration 08 to JODI Supabase database
Fixes schema to match bot code (77-field MVP)
"""

import psycopg2
from pathlib import Path

# JODI Supabase credentials (NOT Ignition Club)
JODI_DB_URL = "postgresql://postgres.herqdldjaxmfusjjpwdg:syO9opxb37SlEV9Q@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

MIGRATION_FILE = Path(__file__).parent / "08_fix_schema_to_match_bot.sql"

def apply_migration():
    print("=" * 80)
    print("JODI Schema Migration 08: Fix Schema to Match Bot")
    print("=" * 80)
    print()
    print(f"📄 Migration file: {MIGRATION_FILE}")
    print(f"🗄️  Database: JODI Supabase (herqdldjaxmfusjjpwdg)")
    print()
    
    # Read migration SQL
    with open(MIGRATION_FILE) as f:
        migration_sql = f.read()
    
    print(f"📝 Migration size: {len(migration_sql)} bytes")
    print()
    
    # Connect to database
    print("🔌 Connecting to database...")
    conn = psycopg2.connect(JODI_DB_URL)
    conn.autocommit = False  # Use transaction
    cursor = conn.cursor()
    
    try:
        print("✅ Connected")
        print()
        print("🚀 Executing migration...")
        print()
        
        # Execute migration
        cursor.execute(migration_sql)
        
        print("✅ Migration executed successfully")
        print()
        
        # Commit transaction
        print("💾 Committing transaction...")
        conn.commit()
        print("✅ Transaction committed")
        print()
        
        # Verify critical columns exist
        print("🔍 Verifying schema changes...")
        print()
        
        # Check users table
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN (
                'looking_for_gender', 'marital_status', 'country_current', 
                'city_current', 'religious_practice', 'work_industry', 
                'diet', 'children_existing', 'body_type'
            )
            ORDER BY column_name;
        """)
        users_cols = [row[0] for row in cursor.fetchall()]
        print(f"✅ Users table sample columns: {users_cols}")
        
        # Check user_preferences table
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user_preferences' 
            AND column_name IN (
                'pref_education_min', 'pref_children_ok', 'partner_location_pref',
                'db_divorced_ok', 'db_widowed_ok', 'caste_importance'
            )
            ORDER BY column_name;
        """)
        prefs_cols = [row[0] for row in cursor.fetchall()]
        print(f"✅ Preferences table sample columns: {prefs_cols}")
        print()
        
        # Check trigger function
        cursor.execute("""
            SELECT pg_get_functiondef(oid)
            FROM pg_proc
            WHERE proname = 'trigger_recalculate_completeness';
        """)
        trigger_def = cursor.fetchone()[0]
        if 'NEW.id' in trigger_def:
            print("✅ Trigger function fixed (uses NEW.id)")
        else:
            print("⚠️  WARNING: Trigger function may still have issues")
        print()
        
        print("=" * 80)
        print("✅ MIGRATION COMPLETE")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Restart JODI bot on Fly.io")
        print("2. Test Q1 (gender) → Q2 (looking_for_gender) flow")
        print("3. Run through all 77 questions to verify completeness")
        
    except Exception as e:
        print()
        print("❌ MIGRATION FAILED")
        print("=" * 80)
        print(f"Error: {e}")
        print()
        print("Rolling back transaction...")
        conn.rollback()
        print("✅ Rollback complete")
        raise
    
    finally:
        cursor.close()
        conn.close()
        print()
        print("🔌 Database connection closed")

if __name__ == "__main__":
    apply_migration()
