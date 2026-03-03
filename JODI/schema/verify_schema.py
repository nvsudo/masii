#!/usr/bin/env python3
"""Verify JODI schema deployment"""

import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres.herqdldjaxmfusjjpwdg:syO9opxb37SlEV9Q@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

def main():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    
    print(f"{GREEN}========================================{NC}")
    print(f"{GREEN}JODI Schema Verification{NC}")
    print(f"{GREEN}========================================{NC}\n")
    
    # 1. Check users table columns
    print(f"{YELLOW}1. Checking users table name columns:{NC}")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('first_name', 'last_name', 'full_name', 'alias')
            ORDER BY column_name;
        """)
        columns = cur.fetchall()
        
        if columns:
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                max_len = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
                print(f"  ✓ {col['column_name']}: {col['data_type']}{max_len} {nullable}")
        else:
            print("  ✗ No name columns found!")
    
    print()
    
    # 2. Check trigger existence
    print(f"{YELLOW}2. Checking auto_generate_full_name trigger:{NC}")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT trigger_name, event_manipulation, action_timing
            FROM information_schema.triggers
            WHERE event_object_table = 'users'
            AND trigger_name = 'auto_generate_full_name';
        """)
        trigger = cur.fetchone()
        
        if trigger:
            print(f"  ✓ Trigger exists: {trigger['trigger_name']}")
            print(f"    - Event: {trigger['event_manipulation']}")
            print(f"    - Timing: {trigger['action_timing']}")
        else:
            print("  ✗ Trigger not found!")
    
    print()
    
    # 3. Test trigger functionality
    print(f"{YELLOW}3. Testing full_name auto-generation trigger:{NC}")
    with conn.cursor() as cur:
        # Create test user
        cur.execute("""
            INSERT INTO users (first_name, last_name, phone_number, whatsapp_id)
            VALUES ('Test', 'User', '+1234567890', 'test_whatsapp_123')
            RETURNING id, first_name, last_name, full_name;
        """)
        test_user = cur.fetchone()
        conn.commit()
        
        if test_user:
            print(f"  ✓ Created test user (ID: {test_user['id']})")
            print(f"    - first_name: {test_user['first_name']}")
            print(f"    - last_name: {test_user['last_name']}")
            print(f"    - full_name: {test_user['full_name']}")
            
            if test_user['full_name'] == 'Test User':
                print(f"  {GREEN}✓ Trigger working correctly!{NC}")
            else:
                print(f"  ✗ Expected 'Test User', got '{test_user['full_name']}'")
            
            # Clean up test user
            cur.execute("DELETE FROM users WHERE id = %s;", (test_user['id'],))
            conn.commit()
            print(f"  ✓ Test user cleaned up")
    
    print()
    
    # 4. Check all tables
    print(f"{YELLOW}4. Verifying all JODI tables:{NC}")
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
        
        for table in tables:
            print(f"  ✓ {table['table_name']} ({table['size']})")
    
    print()
    
    # 5. Check helper functions
    print(f"{YELLOW}5. Checking helper functions:{NC}")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT routine_name, routine_type
            FROM information_schema.routines
            WHERE routine_schema = 'public'
            AND routine_name IN ('calculate_total_completeness', 'check_mvp_activation', 'generate_full_name')
            ORDER BY routine_name;
        """)
        functions = cur.fetchall()
        
        for func in functions:
            print(f"  ✓ {func['routine_name']}() [{func['routine_type']}]")
    
    print()
    print(f"{GREEN}========================================{NC}")
    print(f"{GREEN}Schema verification complete! ✓{NC}")
    print(f"{GREEN}========================================{NC}")
    
    conn.close()

if __name__ == "__main__":
    main()
