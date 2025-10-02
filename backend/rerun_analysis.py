"""Re-run analysis on existing invoices with fixed duplicate detector"""
from app.api.deps.auth import get_supabase_client
from app.services.duplicate_detector import DuplicateDetector
from datetime import datetime, date

supabase = get_supabase_client()

def convert_dates_to_strings(obj):
    """Recursively convert date objects to strings in dictionaries and lists"""
    if isinstance(obj, dict):
        return {key: convert_dates_to_strings(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates_to_strings(item) for item in obj]
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat() if obj else None
    else:
        return obj

print("Re-running analysis with fixed duplicate detector...")

# Get most recent scan
scans = supabase.table('scan_jobs').select('*').order('created_at', desc=True).limit(1).execute()
if not scans.data:
    print("No scans found")
    exit()

scan = scans.data[0]
org_id = scan['org_id']
user_id = scan['user_id']

# Get all invoices
invoices_result = supabase.table('invoices').select('*').eq('org_id', org_id).execute()
all_invoices = invoices_result.data if invoices_result.data else []

print(f"Found {len(all_invoices)} invoices")

# Convert date strings to date objects
for invoice in all_invoices:
    if invoice.get("invoice_date") and isinstance(invoice["invoice_date"], str):
        try:
            invoice["invoice_date"] = datetime.fromisoformat(invoice["invoice_date"]).date()
        except:
            invoice["invoice_date"] = None
    if invoice.get("due_date") and isinstance(invoice["due_date"], str):
        try:
            invoice["due_date"] = datetime.fromisoformat(invoice["due_date"]).date()
        except:
            invoice["due_date"] = None

# Run duplicate detection
detector = DuplicateDetector(duplicate_window_days=7, price_threshold=20.0)

try:
    duplicate_findings = detector.detect_duplicates(all_invoices)
    print(f"[OK] Duplicate detection: {len(duplicate_findings)} findings")

    price_increase_findings = detector.detect_price_increases(all_invoices)
    print(f"[OK] Price increase detection: {len(price_increase_findings)} findings")

    subscription_findings = detector.detect_subscription_sprawl(all_invoices)
    print(f"[OK] Subscription detection: {len(subscription_findings)} findings")

    all_findings = []

    # Convert findings to database records
    finding_invoices_records = []

    for finding in duplicate_findings:
        finding_record = {
            "org_id": org_id,
            "type": "duplicate",
            "title": f"Duplicate charge: {finding.vendor_name}",
            "description": f"{finding.invoice_count} duplicate charges detected",
            "amount": float(finding.amount),
            "confidence_score": finding.confidence_score,
            "status": "pending",
            "details": convert_dates_to_strings(finding.details),
            "primary_invoice_id": finding.invoice_ids[0] if finding.invoice_ids else None,
        }
        all_findings.append((finding_record, finding.invoice_ids))

    for finding in price_increase_findings:
        finding_record = {
            "org_id": org_id,
            "type": "price_increase",
            "title": f"Price increase: {finding.vendor_name}",
            "description": f"{finding.increase_percentage:.1f}% increase detected",
            "amount": float(finding.amount),
            "confidence_score": finding.confidence_score,
            "status": "pending",
            "details": convert_dates_to_strings(finding.details),
            "primary_invoice_id": finding.invoice_ids[0] if finding.invoice_ids else None,
        }
        all_findings.append((finding_record, finding.invoice_ids))

    for finding in subscription_findings:
        invoice_ids = finding.invoice_ids if hasattr(finding, 'invoice_ids') else []
        finding_record = {
            "org_id": org_id,
            "type": "unused_subscription",
            "title": f"Potential subscription issue: {finding.vendor_name}",
            "description": finding.description if hasattr(finding, 'description') else "Review subscription",
            "amount": float(finding.amount),
            "confidence_score": finding.confidence_score,
            "status": "pending",
            "details": convert_dates_to_strings(finding.details if hasattr(finding, 'details') else {}),
            "primary_invoice_id": invoice_ids[0] if invoice_ids else None,
        }
        all_findings.append((finding_record, invoice_ids))

    # Save findings to database
    if all_findings:
        # Insert findings and get IDs
        findings_to_insert = [f[0] for f in all_findings]
        result = supabase.table("findings").insert(findings_to_insert).execute()
        created_findings = result.data

        print(f"\n[OK] Created {len(created_findings)} findings in database")

        # Insert finding_invoices junction records
        junction_records = []
        for i, (_, invoice_ids) in enumerate(all_findings):
            if i < len(created_findings):
                finding_id = created_findings[i]['id']
                for invoice_id in invoice_ids:
                    junction_records.append({
                        "finding_id": finding_id,
                        "invoice_id": invoice_id
                    })

        if junction_records:
            supabase.table("finding_invoices").insert(junction_records).execute()
            print(f"[OK] Created {len(junction_records)} finding-invoice relationships")
    else:
        print("\n[OK] No issues found (no duplicate charges, price increases, or subscription problems)")

    # Update scan job to completed
    supabase.table("scan_jobs").update({
        "status": "completed",
        "error_message": None,
        "completed_at": datetime.utcnow().isoformat(),
    }).eq("id", scan['id']).execute()

    print(f"[OK] Scan job marked as completed")

except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
