#!/usr/bin/env python3
"""
Verify complete setup: Database, Google OAuth, and Supabase configuration
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

print("="*80)
print("VERIFYING COMPLETE SETUP")
print("="*80)

errors = []
warnings = []
success = []

# Check Database
print("\n[1/5] Checking Database Configuration...")
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and "hdkbxjxntgqqmducbmjn.supabase.co" in DATABASE_URL:
    success.append("Database URL configured")
    print("  [OK] DATABASE_URL is set")
else:
    errors.append("DATABASE_URL not properly configured")
    print("  [ERROR] DATABASE_URL missing or invalid")

# Check Supabase
print("\n[2/5] Checking Supabase Configuration...")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if SUPABASE_URL:
    success.append("Supabase URL configured")
    print(f"  [OK] SUPABASE_URL: {SUPABASE_URL}")
else:
    errors.append("SUPABASE_URL missing")
    print("  [ERROR] SUPABASE_URL not set")

if SUPABASE_SERVICE_ROLE_KEY and len(SUPABASE_SERVICE_ROLE_KEY) > 100:
    success.append("Supabase service role key configured")
    print(f"  [OK] SUPABASE_SERVICE_ROLE_KEY is set")
else:
    errors.append("SUPABASE_SERVICE_ROLE_KEY missing or invalid")
    print("  [ERROR] SUPABASE_SERVICE_ROLE_KEY not set")

# Check Google OAuth
print("\n[3/5] Checking Google OAuth Configuration...")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

if GOOGLE_CLIENT_ID and "apps.googleusercontent.com" in GOOGLE_CLIENT_ID:
    success.append("Google Client ID configured")
    print(f"  [OK] GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID[:30]}...")
else:
    errors.append("GOOGLE_CLIENT_ID missing or invalid")
    print("  [ERROR] GOOGLE_CLIENT_ID not set or invalid")

if GOOGLE_CLIENT_SECRET and GOOGLE_CLIENT_SECRET.startswith("GOCSPX-"):
    success.append("Google Client Secret configured")
    print(f"  [OK] GOOGLE_CLIENT_SECRET: {GOOGLE_CLIENT_SECRET[:15]}...")
else:
    errors.append("GOOGLE_CLIENT_SECRET missing or invalid")
    print("  [ERROR] GOOGLE_CLIENT_SECRET not set or invalid")

# Check JWT Secret
print("\n[4/5] Checking JWT Configuration...")
SECRET_KEY = os.getenv("SECRET_KEY")

if SECRET_KEY and len(SECRET_KEY) >= 32:
    success.append("JWT SECRET_KEY configured")
    print(f"  [OK] SECRET_KEY is set (length: {len(SECRET_KEY)})")
else:
    warnings.append("SECRET_KEY not set - needed for JWT tokens")
    print("  [WARNING] SECRET_KEY not set")
    print("  Generate one with: openssl rand -hex 32")

# Check database connection
print("\n[5/5] Testing Database Connection...")
try:
    from supabase import create_client, Client

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    result = supabase.table('organizations').select('*').limit(1).execute()

    success.append("Database connection successful")
    print("  [OK] Connected to Supabase and can query tables")
except Exception as e:
    errors.append(f"Database connection failed: {e}")
    print(f"  [ERROR] Could not connect to database: {e}")

# Summary
print("\n" + "="*80)
print("SETUP VERIFICATION SUMMARY")
print("="*80)

if success:
    print(f"\n[SUCCESS] {len(success)} checks passed:")
    for item in success:
        print(f"  - {item}")

if warnings:
    print(f"\n[WARNING] {len(warnings)} warnings:")
    for item in warnings:
        print(f"  - {item}")

if errors:
    print(f"\n[ERROR] {len(errors)} errors found:")
    for item in errors:
        print(f"  - {item}")
    print("\nPlease fix errors before proceeding.")
    sys.exit(1)
else:
    print("\n" + "="*80)
    print("ALL CHECKS PASSED!")
    print("="*80)

    print("\nYour setup is complete. Remaining manual steps:")
    print("\n1. Supabase Storage Bucket:")
    print("   - Go to: https://supabase.com/dashboard/project/hdkbxjxntgqqmducbmjn/storage/buckets")
    print("   - Create bucket: 'invoice-attachments' (private)")

    print("\n2. Supabase Google OAuth Provider:")
    print("   - Go to: https://supabase.com/dashboard/project/hdkbxjxntgqqmducbmjn/auth/providers")
    print("   - Enable Google provider")
    print("   - Enter Client ID:", GOOGLE_CLIENT_ID)
    print("   - Enter Client Secret:", GOOGLE_CLIENT_SECRET[:15] + "...")

    if warnings:
        print("\n3. Generate JWT Secret Key:")
        print("   Run: openssl rand -hex 32")
        print("   Add to backend/.env as SECRET_KEY")

    print("\n" + "="*80)
    print("READY TO BUILD!")
    print("="*80)
    print("\nYou can now start developing:")
    print("  - Backend API (FastAPI)")
    print("  - Gmail integration")
    print("  - Invoice parsing")
    print("  - Frontend (Next.js)")
    print()
