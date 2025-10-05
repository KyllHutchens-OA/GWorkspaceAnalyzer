"""
Fix stuck scan jobs by marking them as failed
"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Find all stuck scan jobs (queued or processing)
result = supabase.table("scan_jobs").select("*").in_("status", ["queued", "processing"]).execute()

if result.data:
    print(f"Found {len(result.data)} stuck scan jobs:")
    for job in result.data:
        print(f"  - {job['id']} ({job['status']}) - Created: {job['created_at']}")

    # Update them to failed
    update_result = supabase.table("scan_jobs").update({
        "status": "failed",
        "error_message": "Scan interrupted by server restart"
    }).in_("status", ["queued", "processing"]).execute()

    print(f"\nMarked {len(update_result.data)} scan jobs as failed")
else:
    print("No stuck scan jobs found")
