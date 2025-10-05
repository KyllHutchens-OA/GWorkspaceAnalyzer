"""
Test script to monitor scan job progress in real-time
"""
from app.core.config import get_settings
from supabase import create_client
import time

settings = get_settings()
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

# Get the most recent scan job
result = supabase.table('scan_jobs').select('*').order('created_at', desc=True).limit(1).execute()

if result.data:
    job = result.data[0]
    print(f"Monitoring Scan Job: {job['id']}")
    print(f"Initial Status: {job['status']}")
    print(f"Initial Progress: {job['processed_emails']}/{job['total_emails']}")
    print("\nProgress updates:")
    print("-" * 60)

    last_processed = job['processed_emails']
    last_status = job['status']

    while job['status'] in ['queued', 'processing']:
        time.sleep(1)  # Poll every second

        # Get updated job
        result = supabase.table('scan_jobs').select('*').eq('id', job['id']).execute()
        if result.data:
            job = result.data[0]

            # Print update if anything changed
            if job['processed_emails'] != last_processed or job['status'] != last_status:
                progress_pct = (job['processed_emails'] / job['total_emails'] * 100) if job['total_emails'] > 0 else 0
                print(f"{job['status']:<12} | {job['processed_emails']:>4}/{job['total_emails']:<4} | {progress_pct:>5.1f}% | Invoices: {job['invoices_found']}")
                last_processed = job['processed_emails']
                last_status = job['status']

    print("-" * 60)
    print(f"\nFinal Status: {job['status']}")
    print(f"Final Progress: {job['processed_emails']}/{job['total_emails']}")
    print(f"Invoices Found: {job['invoices_found']}")
else:
    print("No scan jobs found")
