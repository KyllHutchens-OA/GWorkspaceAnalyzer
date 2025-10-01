#!/usr/bin/env python3
"""
Deploy database schema to Supabase using PostgREST
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Read migration file
migration_file = Path(__file__).parent / "migrations" / "001_initial_schema.sql"
with open(migration_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

print("="*80)
print("SUPABASE SCHEMA DEPLOYMENT")
print("="*80)
print(f"\nMigration file: {migration_file.name}")
print(f"File size: {len(sql_content):,} bytes")
print(f"Supabase URL: {SUPABASE_URL}")

# Since we can't execute SQL directly via API easily, let's use curl
import subprocess

# Create a temporary SQL file
temp_sql = Path(__file__).parent / "temp_migration.sql"
with open(temp_sql, 'w', encoding='utf-8') as f:
    f.write(sql_content)

print(f"\n{'='*80}")
print("ATTEMPTING DEPLOYMENT VIA CURL...")
print('='*80)

# Try using curl to hit Supabase's database webhook endpoint
# This typically requires the database URL
db_url = DATABASE_URL

# Extract connection details
# postgresql://postgres:password@host:port/database
import re
match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
if not match:
    print("ERROR: Could not parse DATABASE_URL")
    sys.exit(1)

user, password, host, port, database = match.groups()

print(f"Host: {host}")
print(f"Port: {port}")
print(f"Database: {database}")
print(f"User: {user}")

# Check if curl is available
try:
    result = subprocess.run(['curl', '--version'], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception("curl not available")

    print("\nCURL is available. Attempting to execute SQL via Supabase API...")

    # Use Supabase's SQL execution endpoint (if available)
    # This is typically not exposed directly, so we'll need psql

    print("\n" + "="*80)
    print("PSQL CLIENT REQUIRED")
    print("="*80)

    print("\nTo deploy the schema, you have these options:\n")

    print("OPTION 1: Install PostgreSQL client")
    print("-" * 40)
    print("Windows: Download from https://www.postgresql.org/download/windows/")
    print("After installation, run:")
    print(f'  psql "{db_url}" -f "{temp_sql}"')
    print()

    print("OPTION 2: Use Supabase Dashboard (EASIEST)")
    print("-" * 40)
    print("1. Open: https://hdkbxjxntgqqmducbmjn.supabase.co/project/hdkbxjxntgqqmducbmjn/sql")
    print("2. Click 'New Query'")
    print(f"3. Copy contents of: {migration_file}")
    print("4. Paste and click 'Run'")
    print()

    print("OPTION 3: Use online SQL editor")
    print("-" * 40)
    print("I can prepare the SQL and you paste it in the Supabase dashboard.")
    print()

    # Let's just show them the link
    print("="*80)
    print("READY TO DEPLOY")
    print("="*80)
    print("\nClick this link to open Supabase SQL Editor:")
    print(f"https://supabase.com/dashboard/project/hdkbxjxntgqqmducbmjn/sql/new")
    print("\nThen copy/paste this file:")
    print(f"{migration_file.absolute()}")
    print()

except Exception as e:
    print(f"ERROR: {e}")

print("\nAlternatively, I can print the SQL here for you to copy/paste.")
response = input("Print SQL to console? (y/n): ")

if response.lower() == 'y':
    print("\n" + "="*80)
    print("SQL TO EXECUTE")
    print("="*80 + "\n")
    print(sql_content)
