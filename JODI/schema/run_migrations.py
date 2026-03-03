#!/usr/bin/env python3
"""
JODI Schema Migration Runner (Python)
Runs all schema upgrades against Supabase using psycopg2
"""

import psycopg2
import sys
from pathlib import Path

# ANSI colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

DATABASE_URL = "postgresql://postgres.herqdldjaxmfusjjpwdg:syO9opxb37SlEV9Q@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

MIGRATIONS = [
    "01_users_table_upgrade.sql",
    "02_user_signals_table.sql",
    "03_user_preferences_table.sql",
    "04_tier_progress_table.sql",
    "05_matches_table.sql",
    "06_complete_100_datapoints.sql",
    "07_helper_functions.sql",
]

def run_migration(conn, migration_file):
    """Run a single migration file"""
    print(f"{GREEN}Running: {migration_file}{NC}")
    
    sql = Path(migration_file).read_text()
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print(f"{GREEN}✓ Success{NC}\n")
        return True
    except Exception as e:
        print(f"{RED}✗ Failed: {e}{NC}\n")
        conn.rollback()
        return False

def verify_tables(conn):
    """Verify tables were created"""
    print(f"{YELLOW}Verifying tables...{NC}")
    
    query = """
        SELECT 
            table_name,
            pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) AS size
        FROM information_schema.tables
        WHERE table_schema = 'public'
            AND table_name IN ('users', 'user_signals', 'user_preferences', 'tier_progress', 'matches')
        ORDER BY table_name;
    """
    
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()
            
            if results:
                print("\nTables created:")
                for table_name, size in results:
                    print(f"  - {table_name} ({size})")
            else:
                print(f"{RED}No tables found!{NC}")
                
    except Exception as e:
        print(f"{RED}Verification failed: {e}{NC}")

def check_existing_schema(conn):
    """Check what tables/columns already exist"""
    print(f"{YELLOW}Checking existing schema...{NC}")
    
    query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """
    
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()
            
            if results:
                print("Existing tables:")
                for (table_name,) in results:
                    print(f"  - {table_name}")
            else:
                print("No existing tables (fresh database)")
            print()
                
    except Exception as e:
        print(f"{RED}Check failed: {e}{NC}")

def main():
    print(f"{GREEN}========================================{NC}")
    print(f"{GREEN}JODI Schema Migration Runner{NC}")
    print(f"{GREEN}========================================{NC}\n")
    
    # Connect to database
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print(f"{GREEN}✓ Connected to Supabase{NC}\n")
    except Exception as e:
        print(f"{RED}✗ Connection failed: {e}{NC}")
        sys.exit(1)
    
    # Check existing schema
    check_existing_schema(conn)
    
    # Confirm before running
    print(f"{YELLOW}This will modify/create the following tables:{NC}")
    print("  - users (add columns)")
    print("  - user_signals (new table)")
    print("  - user_preferences (new table)")
    print("  - tier_progress (new table)")
    print("  - matches (new table)\n")
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Migration cancelled.")
        sys.exit(0)
    
    print()
    
    # Run migrations
    all_success = True
    for migration in MIGRATIONS:
        if not run_migration(conn, migration):
            all_success = False
            break
    
    if all_success:
        print(f"{GREEN}========================================{NC}")
        print(f"{GREEN}All migrations completed successfully!{NC}")
        print(f"{GREEN}========================================{NC}\n")
        
        # Verify
        verify_tables(conn)
        
        print(f"\n{GREEN}Schema upgrade complete! ✓{NC}")
    else:
        print(f"\n{RED}Migration failed. Check errors above.{NC}")
        sys.exit(1)
    
    conn.close()

if __name__ == "__main__":
    main()
