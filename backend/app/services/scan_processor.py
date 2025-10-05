"""
Scan Job Background Processor
Handles async processing of Gmail scan jobs
"""
import logging
import re
from typing import Dict, Any
from datetime import datetime, date

from supabase import Client

from .gmail_service import GmailService
from .invoice_parser import InvoiceParser
from .duplicate_detector import DuplicateDetector
from ..config import settings

logger = logging.getLogger(__name__)


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


async def process_scan_job(
    job_id: str,
    user: Dict[str, Any],
    supabase: Client,
) -> None:
    """
    Background task to process a scan job

    This function:
    1. Retrieves the scan job from database
    2. Initializes Gmail service with user credentials
    3. Searches for invoice emails in date range
    4. Downloads and parses each email
    5. Extracts invoice data from PDFs
    6. Stores invoices in database
    7. Updates scan job status

    Args:
        job_id: Scan job ID
        user: User dictionary with OAuth credentials
        supabase: Supabase client
    """
    logger.info(f"[SCAN] Starting scan job {job_id} for user {user['id']}")
    print(f"[SCAN] Starting scan job {job_id} for user {user['id']}")

    try:
        # Get scan job details
        job_result = (
            supabase.table("scan_jobs")
            .select("*")
            .eq("id", job_id)
            .execute()
        )

        if not job_result.data or len(job_result.data) == 0:
            logger.error(f"Scan job {job_id} not found")
            return

        job = job_result.data[0]

        # Update job status to processing
        supabase.table("scan_jobs").update({
            "status": "processing",
            "started_at": datetime.utcnow().isoformat(),
        }).eq("id", job_id).execute()

        # Get user OAuth credentials from database
        user_creds_result = (
            supabase.table("users")
            .select("google_access_token, google_refresh_token")
            .eq("id", user["id"])
            .execute()
        )

        if not user_creds_result.data or len(user_creds_result.data) == 0:
            raise Exception("User credentials not found")

        user_creds = user_creds_result.data[0]

        # Initialize Gmail service
        gmail_credentials = {
            "token": user_creds["google_access_token"],
            "refresh_token": user_creds["google_refresh_token"],
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "scopes": settings.GMAIL_SCOPES,
        }

        gmail = GmailService(gmail_credentials)
        parser = InvoiceParser()

        # Parse dates
        start_date = datetime.fromisoformat(job["start_date"])
        end_date = datetime.fromisoformat(job["end_date"])

        # Search for invoice emails
        logger.info(f"Searching emails from {start_date} to {end_date}")
        email_list = gmail.search_invoice_emails(
            start_date=start_date,
            end_date=end_date,
            max_results=500,
        )

        total_emails = len(email_list)
        logger.info(f"Found {total_emails} potential invoice emails")

        # Update total count
        supabase.table("scan_jobs").update({
            "total_emails": total_emails,
        }).eq("id", job_id).execute()

        # Process each email
        processed_count = 0
        invoices_found = 0

        # Calculate update interval for more frequent updates
        # Update every 5 emails OR every 10% of total, whichever is smaller
        update_interval = max(1, min(5, total_emails // 10))

        for email_metadata in email_list:
            try:
                # Get full email details
                email = gmail.get_email_details(email_metadata["id"])

                # Check if it's invoice related
                if not gmail.is_invoice_related(email):
                    processed_count += 1
                    # Update progress at regular intervals
                    if processed_count % update_interval == 0 or processed_count == total_emails:
                        supabase.table("scan_jobs").update({
                            "processed_emails": processed_count,
                            "invoices_found": invoices_found,
                        }).eq("id", job_id).execute()
                    continue

                # Process PDF attachments
                for attachment in email.get("attachments", []):
                    if not attachment["filename"].lower().endswith(".pdf"):
                        continue

                    try:
                        # Download PDF
                        pdf_bytes = gmail.download_attachment(
                            email["id"],
                            attachment["attachment_id"]
                        )

                        # Parse invoice
                        result = parser.parse_pdf(pdf_bytes, attachment["filename"])

                        if result.success and result.invoice:
                            invoice_data = result.invoice

                            # Normalize vendor name for duplicate detection
                            vendor_normalized = re.sub(r'[^a-zA-Z0-9]', '', invoice_data.vendor_name).lower()

                            # Store invoice in database
                            invoice_record = {
                                "user_id": user["id"],
                                "org_id": user.get("org_id"),
                                "scan_job_id": job_id,
                                "gmail_message_id": f"{email['id']}:{attachment['attachment_id']}",  # Make unique per attachment
                                "vendor_name": invoice_data.vendor_name,
                                "vendor_name_normalized": vendor_normalized,
                                "amount": float(invoice_data.amount) if invoice_data.amount else None,
                                "currency": invoice_data.currency,
                                "invoice_number": invoice_data.invoice_number,
                                "invoice_date": invoice_data.invoice_date.isoformat() if invoice_data.invoice_date else None,
                                "due_date": invoice_data.due_date.isoformat() if invoice_data.due_date else None,
                                "raw_text": invoice_data.raw_text,
                                "extraction_method": invoice_data.extraction_method,
                                "confidence_score": invoice_data.confidence_score,
                            }

                            # Check if already exists to prevent duplicates on re-scans
                            existing = supabase.table("invoices").select("id").eq(
                                "gmail_message_id", invoice_record["gmail_message_id"]
                            ).eq("org_id", user.get("org_id")).execute()

                            if not existing.data or len(existing.data) == 0:
                                supabase.table("invoices").insert(invoice_record).execute()
                            invoices_found += 1
                            logger.info(f"Saved invoice from {invoice_data.vendor_name}")

                    except Exception as e:
                        logger.warning(f"Failed to process attachment {attachment['filename']}: {e}")
                        continue

                processed_count += 1

                # Update progress at regular intervals (every 20% of total)
                if processed_count % update_interval == 0 or processed_count == total_emails:
                    supabase.table("scan_jobs").update({
                        "processed_emails": processed_count,
                        "invoices_found": invoices_found,
                    }).eq("id", job_id).execute()

            except Exception as e:
                logger.warning(f"Failed to process email {email_metadata['id']}: {e}")
                processed_count += 1
                # Update progress even on errors
                if processed_count % update_interval == 0 or processed_count == total_emails:
                    supabase.table("scan_jobs").update({
                        "processed_emails": processed_count,
                        "invoices_found": invoices_found,
                    }).eq("id", job_id).execute()
                continue

        # Final progress update to ensure 100%
        supabase.table("scan_jobs").update({
            "processed_emails": processed_count,
            "invoices_found": invoices_found,
        }).eq("id", job_id).execute()

        # Analyze invoices for duplicates and other issues
        logger.info(f"Analyzing {invoices_found} invoices for duplicates and issues...")

        # Fetch all invoices for this user to analyze
        invoices_result = (
            supabase.table("invoices")
            .select("*")
            .eq("user_id", user["id"])
            .execute()
        )

        all_invoices = invoices_result.data if invoices_result.data else []

        # Convert date strings to date objects for duplicate detector
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

        if len(all_invoices) > 0:
            # Run duplicate detection
            detector = DuplicateDetector(duplicate_window_days=7, price_threshold=20.0)

            duplicate_findings = detector.detect_duplicates(all_invoices)
            price_increase_findings = detector.detect_price_increases(all_invoices)
            subscription_findings = detector.detect_subscription_sprawl(all_invoices)

            all_findings = []

            # Convert duplicate findings to database records
            for finding in duplicate_findings:
                finding_record = {
                    "org_id": user.get("org_id"),
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

            # Convert price increase findings
            for finding in price_increase_findings:
                finding_record = {
                    "org_id": user.get("org_id"),
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

            # Convert subscription findings
            for finding in subscription_findings:
                invoice_ids = finding.invoice_ids if hasattr(finding, 'invoice_ids') else []
                finding_record = {
                    "org_id": user.get("org_id"),
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
                # Check for existing findings to avoid duplicates on re-scans
                # Get existing findings for this org
                existing_findings_result = (
                    supabase.table("findings")
                    .select("id, type, primary_invoice_id, status")
                    .eq("org_id", user.get("org_id"))
                    .execute()
                )

                existing_findings_map = {}
                if existing_findings_result.data:
                    for ef in existing_findings_result.data:
                        # Create a key based on type and primary invoice
                        key = f"{ef['type']}:{ef.get('primary_invoice_id')}"
                        existing_findings_map[key] = ef

                # Filter out findings that already exist
                findings_to_insert = []
                findings_metadata = []

                for finding_record, invoice_ids in all_findings:
                    # Check if this finding already exists
                    key = f"{finding_record['type']}:{finding_record.get('primary_invoice_id')}"

                    if key in existing_findings_map:
                        # Finding already exists, skip it
                        logger.debug(f"Skipping duplicate finding: {key}")
                        continue

                    findings_to_insert.append(finding_record)
                    findings_metadata.append(invoice_ids)

                if findings_to_insert:
                    # Insert only new findings
                    result = supabase.table("findings").insert(findings_to_insert).execute()
                    created_findings = result.data

                    logger.info(f"Created {len(created_findings)} new findings (skipped {len(all_findings) - len(findings_to_insert)} existing)")

                    # Insert finding_invoices junction records
                    junction_records = []
                    for i, invoice_ids in enumerate(findings_metadata):
                        if i < len(created_findings):
                            finding_id = created_findings[i]['id']
                            for invoice_id in invoice_ids:
                                junction_records.append({
                                    "finding_id": finding_id,
                                    "invoice_id": invoice_id
                                })

                    if junction_records:
                        supabase.table("finding_invoices").insert(junction_records).execute()
                        logger.info(f"Created {len(junction_records)} finding-invoice relationships")
                else:
                    logger.info(f"No new findings to insert (all {len(all_findings)} findings already exist)")

        # Mark job as completed
        supabase.table("scan_jobs").update({
            "status": "completed",
            "processed_emails": processed_count,
            "invoices_found": invoices_found,
            "completed_at": datetime.utcnow().isoformat(),
        }).eq("id", job_id).execute()

        logger.info(f"Scan job {job_id} completed: {invoices_found} invoices found from {processed_count} emails")

    except Exception as e:
        logger.error(f"Scan job {job_id} failed: {e}")

        # Mark job as failed
        supabase.table("scan_jobs").update({
            "status": "failed",
            "error_message": str(e),
            "completed_at": datetime.utcnow().isoformat(),
        }).eq("id", job_id).execute()
