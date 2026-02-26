#!/usr/bin/env python3
"""Check users table structure"""

import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres.herqdldjaxmfusjjpwdg:syO9opxb37SlEV9Q@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

with conn.cursor() as cur:
    cur.execute("""
        SELECT column_name, data_type, character_maximum_length, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'users'
        ORDER BY ordinal_position;
    """)
    columns = cur.fetchall()
    
    print("Users table structure:")
    print("-" * 80)
    for col in columns:
        nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
        max_len = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
        print(f"{col['column_name']:30s} {col['data_type']}{max_len:20s} {nullable}")

conn.close()
