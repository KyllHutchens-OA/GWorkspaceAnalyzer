"""Check scan results from database"""
from app.api.deps.auth import get_supabase_client
from datetime import datetime, timedelta

supabase = get_supabase_client()

# Get the most recent scan job
scans = supabase.table('scan_jobs').select('*').order('created_at', desc=True).limit(1).execute()

if scans.data:
    scan = scans.data[0]
    print(f'Latest Scan Job:')
    print(f'  ID: {scan["id"]}')
    print(f'  Status: {scan["status"]}')
    print(f'  Emails Found: {scan.get("total_emails", 0)}')
    print(f'  Emails Processed: {scan.get("processed_emails", 0)}')
    print(f'  Invoices Found: {scan.get("invoices_found", 0)}')
    print(f'  Error: {scan.get("error_message")}')
    print()

    # Get invoices for this scan
    org_id = scan['org_id']
    invoices = supabase.table('invoices').select('*').eq('org_id', org_id).execute()
    print(f'Total Invoices in DB: {len(invoices.data) if invoices.data else 0}')

    # Get findings
    findings = supabase.table('findings').select('*').eq('org_id', org_id).execute()
    print(f'Total Findings in DB: {len(findings.data) if findings.data else 0}')

    if invoices.data:
        print(f'\nSample Invoices:')
        for inv in invoices.data[:5]:
            print(f'  - {inv.get("vendor_name")}: ${inv.get("amount")} on {inv.get("invoice_date")}')

    if findings.data:
        print(f'\nFindings:')
        for find in findings.data:
            print(f'  - {find.get("type")}: {find.get("title")} (${find.get("amount")})')
else:
    print('No scans found')
