#!/usr/bin/env python3
"""
Deploy database schema to Supabase using pg8000 (pure Python PostgreSQL client)
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import re

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in .env")
    sys.exit(1)

# Parse connection string
match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
if not match:
    print(f"ERROR: Could not parse DATABASE_URL: {DATABASE_URL}")
    sys.exit(1)

user, password, host, port, database = match.groups()

# Read migration file
migration_file = Path(__file__).parent / "migrations" / "001_initial_schema.sql"
if not migration_file.exists():
    print(f"ERROR: Migration file not found: {migration_file}")
    sys.exit(1)

print(f"Reading migration file: {migration_file}")
with open(migration_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

try:
    import pg8000.native
except ImportError:
    print("Installing pg8000...")
    os.system("pip install pg8000")
    import pg8000.native

print("\n" + "="*80)
print("DEPLOYING DATABASE SCHEMA TO SUPABASE")
print("="*80)
print(f"\nHost: {host}")
print(f"Database: {database}")
print(f"User: {user}")
print(f"Migration: {migration_file.name} ({len(sql_content):,} bytes)")

try:
    # Connect to database
    print("\nConnecting to database...")
    conn = pg8000.native.Connection(
        user=user,
        password=password,
        host=host,
        port=int(port),
        database=database,
        ssl_context=True  # Required for Supabase
    )

    print("Connected successfully!")
    print("\nExecuting migration...")

    # Execute the SQL
    # pg8000 requires autocommit=True for DDL statements
    conn.run(sql_content)

    print("\n" + "="*80)
    print("MIGRATION SUCCESSFUL!")
    print("="*80)

    # Verify tables created
    tables = conn.run("""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
    """)

    print(f"\nTables created ({len(tables)}):")
    for row in tables:
        print(f"  - {row[0]}")

    # Verify RLS policies
    rls_tables = conn.run("""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public' AND rowsecurity = true
        ORDER BY tablename;
    """)

    print(f"\nRow Level Security enabled on {len(rls_tables)} tables:")
    for row in rls_tables:
        print(f"  - {row[0]}")

    # Verify views
    views = conn.run("""
        SELECT viewname
        FROM pg_views
        WHERE schemaname = 'public'
        ORDER BY viewname;
    """)

    print(f"\nViews created ({len(views)}):")
    for row in views:
        print(f"  - {row[0]}")

    # Verify indexes
    indexes = conn.run("""
        SELECT COUNT(*) as index_count
        FROM pg_indexes
        WHERE schemaname = 'public';
    """)

    print(f"\nIndexes created: {indexes[0][0]}")

    # Verify ENUMs
    enums = conn.run("""
        SELECT t.typname
        FROM pg_type t
        JOIN pg_enum e ON t.oid = e.enumtypid
        GROUP BY t.typname
        ORDER BY t.typname;
    """)

    print(f"\nENUM types created ({len(enums)}):")
    for row in enums:
        print(f"  - {row[0]}")

    conn.close()

    print("\n" + "="*80)
    print("DATABASE SETUP COMPLETE!")
    print("="*80)

    print("\nNext steps:")
    print("1. Set up Google OAuth in Supabase Dashboard > Authentication > Providers")
    print("2. Create Storage bucket: invoice-attachments")
    print("3. Set up Supabase Vault for Google refresh tokens")
    print("4. Update .env with Google OAuth credentials")
    print()

except Exception as e:
    print(f"\nERROR: {e}")
    print(f"Type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
