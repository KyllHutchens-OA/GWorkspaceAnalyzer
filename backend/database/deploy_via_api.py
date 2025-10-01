#!/usr/bin/env python3
"""
Deploy database schema to Supabase via REST API
"""
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("ERROR: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
    sys.exit(1)

# Read migration file
migration_file = Path(__file__).parent / "migrations" / "001_initial_schema.sql"
if not migration_file.exists():
    print(f"ERROR: Migration file not found: {migration_file}")
    sys.exit(1)

print(f"Reading migration file: {migration_file}")
with open(migration_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

print(f"\nConnecting to Supabase...")
print(f"URL: {SUPABASE_URL}")

# Execute SQL via Supabase Management API
# Note: This requires direct PostgreSQL access or using Supabase client
# Using supabase-py client instead

try:
    from supabase import create_client, Client
except ImportError:
    print("Installing supabase client...")
    os.system("pip install supabase")
    from supabase import create_client, Client

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

print("\n" + "="*80)
print("DEPLOYING DATABASE SCHEMA VIA SUPABASE API")
print("="*80 + "\n")

# Split SQL into individual statements for execution
statements = []
current_statement = []
in_function = False

for line in sql_content.split('\n'):
    stripped = line.strip()

    # Track if we're inside a function definition
    if 'CREATE OR REPLACE FUNCTION' in line.upper() or 'CREATE FUNCTION' in line.upper():
        in_function = True
    if in_function and stripped.endswith('LANGUAGE plpgsql;'):
        in_function = False
        current_statement.append(line)
        statements.append('\n'.join(current_statement))
        current_statement = []
        continue

    # Skip comments and empty lines
    if not stripped or stripped.startswith('--'):
        continue

    current_statement.append(line)

    # End of statement (but not if inside function)
    if not in_function and stripped.endswith(';') and not stripped.startswith('--'):
        statements.append('\n'.join(current_statement))
        current_statement = []

# Add any remaining statement
if current_statement:
    statements.append('\n'.join(current_statement))

print(f"Found {len(statements)} SQL statements to execute")

# Note: Supabase Python client doesn't have direct SQL execution
# We need to use the REST API endpoint or run via Supabase dashboard

print("\n" + "="*80)
print("MANUAL DEPLOYMENT REQUIRED")
print("="*80 + "\n")

print("The Supabase Python client doesn't support direct SQL execution.")
print("\nPlease deploy using one of these methods:\n")

print("METHOD 1: Supabase Dashboard (RECOMMENDED)")
print("-" * 40)
print("1. Go to: https://hdkbxjxntgqqmducbmjn.supabase.co")
print("2. Navigate to: SQL Editor")
print("3. Click: New Query")
print("4. Copy/paste contents of:")
print(f"   {migration_file}")
print("5. Click: Run (or Ctrl+Enter)\n")

print("METHOD 2: Copy SQL to clipboard")
print("-" * 40)
print("The SQL has been prepared. Would you like me to:")
print("a) Copy it to clipboard")
print("b) Show you the first 50 lines")
print("c) Save to a simplified file\n")

# Write a simplified single-file version
output_file = Path(__file__).parent / "deploy_me.sql"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(sql_content)

print(f"Full SQL saved to: {output_file}")
print("\nYou can copy this file contents and paste into Supabase SQL Editor.\n")
