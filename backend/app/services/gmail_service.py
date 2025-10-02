"""
Gmail API Service
Handles all Gmail API interactions for scanning and retrieving emails
"""
import base64
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..config import settings

logger = logging.getLogger(__name__)


class GmailService:
    """
    Gmail API service for scanning emails and retrieving invoice data
    """

    def __init__(self, user_credentials: Dict[str, str]):
        """
        Initialize Gmail service with user OAuth credentials

        Args:
            user_credentials: Dict containing OAuth tokens
                {
                    "token": "access_token",
                    "refresh_token": "refresh_token",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "client_id": "...",
                    "client_secret": "...",
                    "scopes": [...]
                }
        """
        self.credentials = Credentials(
            token=user_credentials.get("token"),
            refresh_token=user_credentials.get("refresh_token"),
            token_uri=user_credentials.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=user_credentials.get("client_id", settings.GOOGLE_CLIENT_ID),
            client_secret=user_credentials.get("client_secret", settings.GOOGLE_CLIENT_SECRET),
            scopes=user_credentials.get("scopes", settings.GMAIL_SCOPES),
        )

        self.service = build("gmail", "v1", credentials=self.credentials)

    def search_invoice_emails(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_results: int = 500,
    ) -> List[Dict[str, Any]]:
        """
        Search for emails that likely contain invoices or receipts

        Args:
            start_date: Start date for search (default: 90 days ago)
            end_date: End date for search (default: today)
            max_results: Maximum number of results to return

        Returns:
            List of email metadata dictionaries
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=90)
        if not end_date:
            end_date = datetime.now()

        # Build search query for invoice-related emails
        query = self._build_invoice_query(start_date, end_date)

        try:
            results = []
            page_token = None

            while len(results) < max_results:
                response = (
                    self.service.users()
                    .messages()
                    .list(
                        userId="me",
                        q=query,
                        maxResults=min(100, max_results - len(results)),
                        pageToken=page_token,
                    )
                    .execute()
                )

                messages = response.get("messages", [])
                if not messages:
                    break

                results.extend(messages)

                page_token = response.get("nextPageToken")
                if not page_token:
                    break

            logger.info(f"Found {len(results)} potential invoice emails")
            return results

        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            raise

    def _build_invoice_query(self, start_date: datetime, end_date: datetime) -> str:
        """
        Build Gmail search query to find invoice/receipt emails

        Args:
            start_date: Start date for search
            end_date: End date for search

        Returns:
            Gmail search query string
        """
        # Format dates for Gmail query (YYYY/MM/DD)
        after = start_date.strftime("%Y/%m/%d")
        before = end_date.strftime("%Y/%m/%d")

        # Keywords that commonly appear in invoice emails
        keywords = [
            "invoice",
            "receipt",
            "payment",
            "billing",
            "order confirmation",
            "purchase",
            "subscription",
            "charge",
            "paid",
        ]

        # File types that often contain invoices
        file_types = ["pdf", "jpg", "png", "jpeg"]

        # Build query components
        keyword_query = " OR ".join(keywords)
        attachment_query = " OR ".join([f"filename:{ft}" for ft in file_types])

        # Combine into final query
        # Look for emails with keywords OR attachments, within date range
        query = (
            f"({keyword_query}) OR ({attachment_query}) "
            f"after:{after} before:{before} "
            f"has:attachment OR subject:(invoice OR receipt OR billing)"
        )

        return query

    def get_email_details(self, message_id: str) -> Dict[str, Any]:
        """
        Get full details of an email including body and attachments

        Args:
            message_id: Gmail message ID

        Returns:
            Dictionary with email details
        """
        try:
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )

            # Extract email metadata
            headers = message["payload"]["headers"]
            subject = self._get_header(headers, "Subject")
            sender = self._get_header(headers, "From")
            date = self._get_header(headers, "Date")
            to = self._get_header(headers, "To")

            # Extract email body
            body = self._extract_email_body(message["payload"])

            # Extract attachments
            attachments = self._extract_attachments(message)

            return {
                "id": message["id"],
                "thread_id": message["threadId"],
                "subject": subject,
                "from": sender,
                "to": to,
                "date": date,
                "body": body,
                "attachments": attachments,
                "labels": message.get("labelIds", []),
                "snippet": message.get("snippet", ""),
            }

        except HttpError as error:
            logger.error(f"Error fetching email {message_id}: {error}")
            raise

    def _get_header(self, headers: List[Dict], name: str) -> str:
        """Extract header value by name"""
        for header in headers:
            if header["name"].lower() == name.lower():
                return header["value"]
        return ""

    def _extract_email_body(self, payload: Dict) -> str:
        """
        Extract text body from email payload

        Args:
            payload: Email payload from Gmail API

        Returns:
            Email body as plain text
        """
        body = ""

        # Check for body in payload
        if "body" in payload and "data" in payload["body"]:
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
        # Check for body in parts (multipart emails)
        elif "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain" and "data" in part["body"]:
                    body += base64.urlsafe_b64decode(part["body"]["data"]).decode(
                        "utf-8"
                    )
                elif part["mimeType"] == "text/html" and "data" in part["body"]:
                    # Store HTML body if no plain text found
                    if not body:
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode(
                            "utf-8"
                        )
                # Recursively check nested parts
                elif "parts" in part:
                    body += self._extract_email_body(part)

        return body

    def _extract_attachments(self, message: Dict) -> List[Dict[str, Any]]:
        """
        Extract attachment metadata from email

        Args:
            message: Full email message from Gmail API

        Returns:
            List of attachment metadata dictionaries
        """
        attachments = []

        if "payload" in message and "parts" in message["payload"]:
            for part in message["payload"]["parts"]:
                if part.get("filename"):
                    attachment = {
                        "filename": part["filename"],
                        "mime_type": part["mimeType"],
                        "size": part["body"].get("size", 0),
                        "attachment_id": part["body"].get("attachmentId"),
                    }
                    attachments.append(attachment)

        return attachments

    def download_attachment(
        self, message_id: str, attachment_id: str
    ) -> bytes:
        """
        Download an email attachment

        Args:
            message_id: Gmail message ID
            attachment_id: Attachment ID from email

        Returns:
            Attachment data as bytes
        """
        try:
            attachment = (
                self.service.users()
                .messages()
                .attachments()
                .get(userId="me", messageId=message_id, id=attachment_id)
                .execute()
            )

            data = attachment["data"]
            file_data = base64.urlsafe_b64decode(data)

            return file_data

        except HttpError as error:
            logger.error(f"Error downloading attachment: {error}")
            raise

    def get_user_profile(self) -> Dict[str, str]:
        """
        Get the authenticated user's Gmail profile

        Returns:
            Dictionary with user profile info
        """
        try:
            profile = self.service.users().getProfile(userId="me").execute()

            return {
                "email": profile["emailAddress"],
                "messages_total": profile.get("messagesTotal", 0),
                "threads_total": profile.get("threadsTotal", 0),
            }

        except HttpError as error:
            logger.error(f"Error fetching user profile: {error}")
            raise

    def batch_get_emails(self, message_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Efficiently fetch multiple emails in batch

        Args:
            message_ids: List of Gmail message IDs

        Returns:
            List of email details dictionaries
        """
        emails = []

        # Gmail API batch requests (max 100 per batch)
        batch_size = 100

        for i in range(0, len(message_ids), batch_size):
            batch = message_ids[i : i + batch_size]

            for msg_id in batch:
                try:
                    email = self.get_email_details(msg_id)
                    emails.append(email)
                except HttpError as e:
                    logger.warning(f"Failed to fetch email {msg_id}: {e}")
                    continue

        logger.info(f"Successfully fetched {len(emails)} out of {len(message_ids)} emails")
        return emails

    def is_invoice_related(self, email: Dict[str, Any]) -> bool:
        """
        Determine if an email is likely invoice/receipt related

        Args:
            email: Email details dictionary

        Returns:
            True if email appears to be invoice-related (excludes quotes)
        """
        # Keywords to look for
        invoice_keywords = [
            "invoice",
            "receipt",
            "payment",
            "billing",
            "order",
            "purchase",
            "subscription",
            "charge",
            "total",
            "amount due",
            "paid",
        ]

        # Keywords that indicate this is NOT an invoice (quote/estimate)
        quote_keywords = [
            "quote",
            "quotation",
            "estimate",
            "proposal",
            "pro forma",
            "proforma",
        ]

        # Check subject
        subject = email.get("subject", "").lower()

        # Exclude quotes/estimates
        if any(keyword in subject for keyword in quote_keywords):
            return False

        if any(keyword in subject for keyword in invoice_keywords):
            return True

        # Check body
        body = email.get("body", "").lower()

        # Exclude quotes/estimates
        if any(keyword in body for keyword in quote_keywords):
            return False

        if any(keyword in body for keyword in invoice_keywords):
            return True

        # Check for PDF attachments (common for invoices)
        attachments = email.get("attachments", [])
        for att in attachments:
            filename_lower = att["filename"].lower()

            # Exclude if filename contains quote/estimate keywords
            if any(keyword in filename_lower for keyword in quote_keywords):
                return False

            # Include if it's a PDF or has invoice in the name
            if filename_lower.endswith(".pdf") or "invoice" in filename_lower:
                return True

        return False
