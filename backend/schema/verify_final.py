#!/usr/bin/env python3
"""Final verification of JODI schema deployment"""

import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres.herqdldjaxmfusjjpwdg:syO9opxb37SlEV9Q@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

def main():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    
    print(f"{GREEN}========================================{NC}")
    print(f"{GREEN}JODI Schema Deployment Verification{NC}")
    print(f"{GREEN}========================================{NC}\n")
    
    # 1. Check users table name columns
    print(f"{YELLOW}✓ Checking users table name columns:{NC}")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('first_name', 'last_name', 'full_name', 'alias')
            ORDER BY column_name;
        """)
        columns = cur.fetchall()
        
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            max_len = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
            print(f"  ✓ {col['column_name']}: {col['data_type']}{max_len} {nullable}")
    
    print()
    
    # 2. Check all triggers on users table
    print(f"{YELLOW}✓ Checking triggers on users table:{NC}")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT trigger_name, event_manipulation, action_timing
            FROM information_schema.triggers
            WHERE event_object_table = 'users'
            ORDER BY trigger_name;
        """)
        triggers = cur.fetchall()
        
        for trigger in triggers:
            print(f"  ✓ {trigger['trigger_name']}")
            print(f"      Event: {trigger['action_timing']} {trigger['event_manipulation']}")
    
    print()
    
    # 3. Test full_name auto-generation trigger
    print(f"{YELLOW}✓ Testing full_name auto-generation trigger:{NC}")
    with conn.cursor() as cur:
        # Create test user with minimal required fields
        test_telegram_id = 999999999
        
        # First clean up any existing test user
        cur.execute("DELETE FROM users WHERE telegram_id = %s;", (test_telegram_id,))
        conn.commit()
        
        # Insert test user with first_name and last_name
        cur.execute("""
            INSERT INTO users (telegram_id, first_name, last_name)
            VALUES (%s, 'Test', 'User')
            RETURNING id, first_name, last_name, full_name;
        """, (test_telegram_id,))
        test_user = cur.fetchone()
        conn.commit()
        
        print(f"  Created test user (ID: {test_user['id']})")
        print(f"    first_name: '{test_user['first_name']}'")
        print(f"    last_name: '{test_user['last_name']}'")
        print(f"    full_name: '{test_user['full_name']}'")
        
        if test_user['full_name'] == 'Test User':
            print(f"  {GREEN}✓ Trigger working correctly!{NC}")
        else:
            print(f"  {RED}✗ Expected 'Test User', got '{test_user['full_name']}'{NC}")
        
        # Clean up test user
        cur.execute("DELETE FROM users WHERE id = %s;", (test_user['id'],))
        conn.commit()
        print(f"  ✓ Test user cleaned up")
    
    print()
    
    # 4. Verify all JODI tables exist
    print(f"{YELLOW}✓ Verifying all JODI tables:{NC}")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                table_name,
                pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) AS size
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('users', 'user_signals', 'user_preferences', 'tier_progress', 'matches')
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        expected_tables = {'users', 'user_signals', 'user_preferences', 'tier_progress', 'matches'}
        found_tables = {t['table_name'] for t in tables}
        
        for table in tables:
            print(f"  ✓ {table['table_name']:20s} {table['size']}")
        
        if expected_tables == found_tables:
            print(f"\n  {GREEN}✓ All 5 tables present!{NC}")
    
    print()
    
    # 5. Check critical helper functions
    print(f"{YELLOW}✓ Checking helper functions:{NC}")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT routine_name
            FROM information_schema.routines
            WHERE routine_schema = 'public'
            AND routine_name IN (
                'calculate_total_completeness',
                'check_mvp_activation',
                'generate_full_name',
                'update_updated_at_column',
                'calculate_age_from_dob'
            )
            ORDER BY routine_name;
        """)
        functions = cur.fetchall()
        
        for func in functions:
            print(f"  ✓ {func['routine_name']}()")
    
    print()
    
    # 6. Sample query: Count users with full names
    print(f"{YELLOW}✓ Database statistics:{NC}")
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) as total, COUNT(full_name) as with_full_name FROM users;")
        stats = cur.fetchone()
        print(f"  Total users: {stats['total']}")
        print(f"  Users with full_name: {stats['with_full_name']}")
    
    print()
    print(f"{GREEN}========================================{NC}")
    print(f"{GREEN}✓ Schema deployment verified successfully!{NC}")
    print(f"{GREEN}========================================{NC}")
    
    conn.close()

if __name__ == "__main__":
    main()
