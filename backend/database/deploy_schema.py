#!/usr/bin/env python3
"""
Deploy database schema to Supabase
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import psycopg2
    from dotenv import load_dotenv
except ImportError:
    print("Installing required packages...")
    os.system("pip install psycopg2-binary python-dotenv")
    import psycopg2
    from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in .env file")
    sys.exit(1)

# Read migration file
migration_file = Path(__file__).parent / "migrations" / "001_initial_schema.sql"
if not migration_file.exists():
    print(f"ERROR: Migration file not found: {migration_file}")
    sys.exit(1)

print(f"Reading migration file: {migration_file}")
with open(migration_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

print(f"Connecting to database...")
print(f"Database URL: {DATABASE_URL[:50]}...")

try:
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("DEPLOYING DATABASE SCHEMA")
    print("="*80 + "\n")

    # Execute migration
    cursor.execute(sql_content)

    # Commit transaction
    conn.commit()

    print("\n" + "="*80)
    print("✅ MIGRATION SUCCESSFUL")
    print("="*80 + "\n")

    # Verify tables created
    cursor.execute("""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
    """)

    tables = cursor.fetchall()
    print(f"📊 Tables created ({len(tables)}):")
    for table in tables:
        print(f"   - {table[0]}")

    # Verify RLS policies
    cursor.execute("""
        SELECT tablename, rowsecurity
        FROM pg_tables
        WHERE schemaname = 'public' AND rowsecurity = true
        ORDER BY tablename;
    """)

    rls_tables = cursor.fetchall()
    print(f"\n🔒 Row Level Security enabled on {len(rls_tables)} tables:")
    for table in rls_tables:
        print(f"   - {table[0]}")

    # Verify indexes
    cursor.execute("""
        SELECT indexname, tablename
        FROM pg_indexes
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname;
    """)

    indexes = cursor.fetchall()
    print(f"\n⚡ Indexes created ({len(indexes)}):")
    index_count = {}
    for idx_name, tbl_name in indexes:
        if tbl_name not in index_count:
            index_count[tbl_name] = 0
        index_count[tbl_name] += 1

    for tbl_name, count in sorted(index_count.items()):
        print(f"   - {tbl_name}: {count} indexes")

    # Verify views
    cursor.execute("""
        SELECT viewname
        FROM pg_views
        WHERE schemaname = 'public'
        ORDER BY viewname;
    """)

    views = cursor.fetchall()
    print(f"\n📈 Views created ({len(views)}):")
    for view in views:
        print(f"   - {view[0]}")

    cursor.close()
    conn.close()

    print("\n" + "="*80)
    print("🎉 DATABASE SETUP COMPLETE")
    print("="*80 + "\n")

    print("Next steps:")
    print("1. Set up Google OAuth provider in Supabase Dashboard")
    print("2. Configure Storage bucket for invoice attachments")
    print("3. Set up Supabase Vault for Google refresh tokens")
    print("4. Update environment variables with Google OAuth credentials\n")

except psycopg2.Error as e:
    print(f"\n❌ DATABASE ERROR:")
    print(f"   {e}")
    if conn:
        conn.rollback()
        conn.close()
    sys.exit(1)
except Exception as e:
    print(f"\n❌ ERROR:")
    print(f"   {e}")
    if conn:
        conn.rollback()
        conn.close()
    sys.exit(1)
