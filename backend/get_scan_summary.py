"""Get detailed scan summary"""
from app.api.deps.auth import get_supabase_client

supabase = get_supabase_client()

# Get most recent scan
scans = supabase.table('scan_jobs').select('*').order('created_at', desc=True).limit(1).execute()
if not scans.data:
    print("No scans found")
    exit()

scan = scans.data[0]
org_id = scan['org_id']

print("=" * 70)
print("SCAN SUMMARY")
print("=" * 70)
print(f"Status: {scan['status']}")
print(f"Started: {scan.get('started_at')}")
print(f"Completed: {scan.get('completed_at')}")
print()

print("EMAIL PROCESSING:")
print(f"  Total emails found: {scan.get('total_emails', 0)}")
print(f"  Emails processed: {scan.get('processed_emails', 0)}")
print(f"  Invoices extracted: {scan.get('invoices_found', 0)}")
print(f"  Success rate: {scan.get('invoices_found', 0) / scan.get('processed_emails', 1) * 100:.1f}%")
print()

# Get invoices for this scan
invoices = supabase.table('invoices').select('*').eq('scan_job_id', scan['id']).execute()
print(f"INVOICES FROM THIS SCAN: {len(invoices.data) if invoices.data else 0}")

if invoices.data:
    # Count by extraction method
    extraction_methods = {}
    for inv in invoices.data:
        method = inv.get('extraction_method', 'unknown')
        extraction_methods[method] = extraction_methods.get(method, 0) + 1

    print("\nExtraction Methods:")
    for method, count in extraction_methods.items():
        print(f"  {method}: {count}")

    # Count unknown vendors
    unknown_count = sum(1 for inv in invoices.data if inv.get('vendor_name') == 'Unknown Vendor')
    print(f"\nVendors:")
    print(f"  Known: {len(invoices.data) - unknown_count}")
    print(f"  Unknown: {unknown_count}")

    # Show sample of successfully extracted
    print("\nSample Successfully Extracted:")
    known_vendors = [inv for inv in invoices.data if inv.get('vendor_name') != 'Unknown Vendor']
    for inv in known_vendors[:5]:
        print(f"  - {inv.get('vendor_name')}: ${inv.get('amount')} on {inv.get('invoice_date')}")

# Get findings
findings = supabase.table('findings').select('*').eq('org_id', org_id).execute()
print(f"\nFINDINGS: {len(findings.data) if findings.data else 0}")

if findings.data:
    by_type = {}
    for finding in findings.data:
        ftype = finding.get('type', 'unknown')
        by_type[ftype] = by_type.get(ftype, 0) + 1

    print("\nBy Type:")
    for ftype, count in by_type.items():
        print(f"  {ftype}: {count}")

    total_waste = sum(finding.get('amount', 0) for finding in findings.data if finding.get('status') == 'pending')
    print(f"\nPotential Savings: ${total_waste:,.2f}")

print("\n" + "=" * 70)
