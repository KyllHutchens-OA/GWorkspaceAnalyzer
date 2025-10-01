"""
Scan Job Background Processor
Handles async processing of Gmail scan jobs
"""
import logging
from typing import Dict, Any
from datetime import datetime, date

from supabase import Client

from .gmail_service import GmailService
from .invoice_parser import InvoiceParser
from ..config import settings

logger = logging.getLogger(__name__)


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
    logger.info(f"Starting scan job {job_id} for user {user['id']}")

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

        for email_metadata in email_list:
            try:
                # Get full email details
                email = gmail.get_email_details(email_metadata["id"])

                # Check if it's invoice related
                if not gmail.is_invoice_related(email):
                    processed_count += 1
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

                            # Store invoice in database
                            invoice_record = {
                                "user_id": user["id"],
                                "org_id": user.get("org_id"),
                                "scan_job_id": job_id,
                                "email_id": email["id"],
                                "vendor_name": invoice_data.vendor_name,
                                "amount": float(invoice_data.amount) if invoice_data.amount else None,
                                "currency": invoice_data.currency,
                                "invoice_number": invoice_data.invoice_number,
                                "invoice_date": invoice_data.invoice_date.isoformat() if invoice_data.invoice_date else None,
                                "due_date": invoice_data.due_date.isoformat() if invoice_data.due_date else None,
                                "raw_text": invoice_data.raw_text,
                                "extraction_method": invoice_data.extraction_method,
                                "confidence_score": invoice_data.confidence_score,
                            }

                            supabase.table("invoices").insert(invoice_record).execute()
                            invoices_found += 1
                            logger.info(f"Saved invoice from {invoice_data.vendor_name}")

                    except Exception as e:
                        logger.warning(f"Failed to process attachment {attachment['filename']}: {e}")
                        continue

                processed_count += 1

                # Update progress every 10 emails
                if processed_count % 10 == 0:
                    supabase.table("scan_jobs").update({
                        "processed_emails": processed_count,
                        "invoices_found": invoices_found,
                    }).eq("id", job_id).execute()

            except Exception as e:
                logger.warning(f"Failed to process email {email_metadata['id']}: {e}")
                processed_count += 1
                continue

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
