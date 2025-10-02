"""
Invoice Parsing Service
Extracts structured data from PDFs, emails, and attachments using GPT-4o Mini
"""
import re
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from io import BytesIO

import PyPDF2
import pdfplumber
from dateutil import parser as date_parser

from ..models import ParsedInvoice, InvoiceExtractionResult, LineItem
from .gpt_extractor import GPTInvoiceExtractor

logger = logging.getLogger(__name__)


class InvoiceParser:
    """
    Parses invoices from various sources (PDF, HTML, plain text)
    and extracts structured data using GPT-4o Mini
    """

    def __init__(self, use_gpt: bool = True):
        """
        Initialize invoice parser

        Args:
            use_gpt: Use GPT-4o Mini for extraction (default: True)
        """
        self.use_gpt = use_gpt
        if use_gpt:
            try:
                self.gpt_extractor = GPTInvoiceExtractor()
            except Exception as e:
                logger.warning(f"Failed to initialize GPT extractor: {e}. Falling back to regex.")
                self.gpt_extractor = None
                self.use_gpt = False
        else:
            self.gpt_extractor = None

    # Common vendor name patterns (fallback for regex mode)
    VENDOR_PATTERNS = [
        r"^([A-Z][A-Za-z\s&,.]+?)(?:\n|\r|$)",  # First line (common for invoices)
        r"from[:\s]+([A-Z][A-Za-z\s&,.]+?)(?:\n|$)",
        r"invoice from[:\s]+([A-Z][A-Za-z\s&,.]+?)(?:\n|$)",
        r"^([A-Z][A-Za-z\s&,.]+?)\s*(?:Inc\.?|LLC|Ltd\.?|Corporation|Pty)",
    ]

    # Amount patterns (matches $1,234.56, 1234.56, etc.)
    AMOUNT_PATTERNS = [
        r"(?:TOTAL|Total)[:\s]*\$\s*(\d[\d,]*\.\d{2})",  # TOTAL: $2,499.00
        r"(?:total|amount|due|balance)[:\s]*\$\s*(\d[\d,]*\.\d{2})",
        r"\$\s*(\d[\d,]*\.\d{2})",  # $1,234.56
        r"(\d[\d,]*\.\d{2})\s*(?:USD|usd)",
    ]

    # Invoice number patterns
    INVOICE_NUMBER_PATTERNS = [
        r"Invoice\s+Number[:\s]+([A-Z0-9-]+)",  # Invoice Number: AWS-12345
        r"invoice\s+number[:\s]+([A-Z0-9-]+)",
        r"Invoice\s*#[:\s]*([A-Z0-9-]+)",  # Invoice #AWS-12345
        r"invoice\s*#[:\s]*([A-Z0-9-]+)",
        r"#\s*([A-Z0-9-]{5,})",
    ]

    # Date patterns
    DATE_PATTERNS = [
        r"date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"invoice\s+date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})",
        r"(\w+\s+\d{1,2},\s+\d{4})",
    ]

    def parse_pdf(self, pdf_bytes: bytes, filename: str = "") -> InvoiceExtractionResult:
        """
        Parse invoice data from PDF file using GPT-4o Mini

        Args:
            pdf_bytes: PDF file as bytes
            filename: Original filename (for metadata)

        Returns:
            InvoiceExtractionResult with parsed data
        """
        start_time = datetime.now()

        try:
            # Extract text from PDF
            text = self._extract_text_pdfplumber(pdf_bytes)

            if not text or len(text) < 50:
                # Fallback to PyPDF2
                text = self._extract_text_pypdf2(pdf_bytes)

            if not text or len(text) < 20:
                return InvoiceExtractionResult(
                    success=False,
                    error="Could not extract text from PDF",
                    source_type="pdf",
                )

            # Parse with GPT or regex
            if self.use_gpt and self.gpt_extractor:
                logger.info("Using GPT-4o Mini for invoice extraction")
                invoice = self.gpt_extractor.extract_invoice_data(text)
            else:
                logger.info("Using regex for invoice extraction (GPT disabled)")
                invoice = self._parse_text(text)
                invoice.extraction_method = "pdf_regex"

            invoice.raw_text = text[:5000]  # Store first 5000 chars

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return InvoiceExtractionResult(
                success=True,
                invoice=invoice,
                source_type="pdf",
                processing_time_ms=int(processing_time),
            )

        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            return InvoiceExtractionResult(
                success=False,
                error=str(e),
                source_type="pdf",
            )

    def _extract_text_pdfplumber(self, pdf_bytes: bytes) -> str:
        """Extract text using pdfplumber"""
        try:
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
            return ""

    def _extract_text_pypdf2(self, pdf_bytes: bytes) -> str:
        """Extract text using PyPDF2 (fallback)"""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {e}")
            return ""

    def parse_email_html(self, html: str) -> InvoiceExtractionResult:
        """
        Parse invoice data from HTML email

        Args:
            html: HTML email content

        Returns:
            InvoiceExtractionResult with parsed data
        """
        start_time = datetime.now()

        try:
            # Strip HTML tags to get plain text
            text = self._html_to_text(html)

            invoice = self._parse_text(text)
            invoice.extraction_method = "html"
            invoice.raw_text = text[:5000]

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return InvoiceExtractionResult(
                success=True,
                invoice=invoice,
                source_type="email_html",
                processing_time_ms=int(processing_time),
            )

        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return InvoiceExtractionResult(
                success=False,
                error=str(e),
                source_type="email_html",
            )

    def parse_email_text(self, text: str) -> InvoiceExtractionResult:
        """
        Parse invoice data from plain text email

        Args:
            text: Plain text email content

        Returns:
            InvoiceExtractionResult with parsed data
        """
        start_time = datetime.now()

        try:
            invoice = self._parse_text(text)
            invoice.extraction_method = "email_text"
            invoice.raw_text = text[:5000]

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return InvoiceExtractionResult(
                success=True,
                invoice=invoice,
                source_type="email_text",
                processing_time_ms=int(processing_time),
            )

        except Exception as e:
            logger.error(f"Error parsing text: {e}")
            return InvoiceExtractionResult(
                success=False,
                error=str(e),
                source_type="email_text",
            )

    def _parse_text(self, text: str) -> ParsedInvoice:
        """
        Core parsing logic - extracts invoice data from text

        Args:
            text: Raw text content

        Returns:
            ParsedInvoice with extracted data
        """
        # Extract vendor name
        vendor = self._extract_vendor(text)

        # Extract amounts
        amounts = self._extract_amounts(text)
        total_amount = amounts[0] if amounts else Decimal("0.00")

        # Extract invoice number
        invoice_number = self._extract_invoice_number(text)

        # Extract dates
        invoice_date = self._extract_date(text, "invoice")
        due_date = self._extract_date(text, "due")

        # Calculate confidence score
        confidence = self._calculate_confidence(
            vendor=vendor,
            amount=total_amount,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
        )

        return ParsedInvoice(
            vendor_name=vendor or "Unknown Vendor",
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=due_date,
            amount=total_amount,
            currency="USD",
            confidence_score=confidence,
        )

    def _extract_vendor(self, text: str) -> Optional[str]:
        """Extract vendor name from text"""
        text_upper = text[:500]  # Check first 500 chars

        for pattern in self.VENDOR_PATTERNS:
            match = re.search(pattern, text_upper, re.IGNORECASE | re.MULTILINE)
            if match:
                vendor = match.group(1).strip()
                # Clean up vendor name
                vendor = re.sub(r'\s+', ' ', vendor)
                if len(vendor) > 3:  # Minimum length
                    return vendor

        # Fallback: try to find email sender pattern
        email_match = re.search(r'from[:\s]+([a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})', text, re.IGNORECASE)
        if email_match:
            email = email_match.group(1)
            # Extract domain as vendor name
            domain = email.split('@')[1].split('.')[0]
            return domain.capitalize()

        return None

    def _extract_amounts(self, text: str) -> List[Decimal]:
        """Extract monetary amounts from text"""
        amounts = []

        for pattern in self.AMOUNT_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = Decimal(amount_str)
                    if amount > 0:
                        amounts.append(amount)
                except (ValueError, ArithmeticError):
                    continue

        # Sort by value (descending) - total is usually the largest
        amounts.sort(reverse=True)
        return amounts

    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number from text"""
        text_sample = text[:1000]  # Check first 1000 chars

        for pattern in self.INVOICE_NUMBER_PATTERNS:
            match = re.search(pattern, text_sample, re.IGNORECASE)
            if match:
                invoice_num = match.group(1).strip()
                if len(invoice_num) >= 3:  # Minimum length
                    return invoice_num

        return None

    def _extract_date(self, text: str, date_type: str = "invoice") -> Optional[date]:
        """
        Extract date from text

        Args:
            text: Text to search
            date_type: "invoice" or "due"

        Returns:
            Parsed date or None
        """
        text_sample = text[:1000]

        # Build specific pattern based on date type
        if date_type == "due":
            specific_patterns = [
                r"due\s+date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"payment\s+due\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            ]
        else:
            specific_patterns = self.DATE_PATTERNS

        for pattern in specific_patterns:
            match = re.search(pattern, text_sample, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    parsed_date = date_parser.parse(date_str, fuzzy=True)
                    return parsed_date.date()
                except (ValueError, TypeError):
                    continue

        return None

    def _calculate_confidence(
        self,
        vendor: Optional[str],
        amount: Decimal,
        invoice_number: Optional[str],
        invoice_date: Optional[date],
    ) -> float:
        """
        Calculate confidence score for extraction

        Args:
            vendor: Extracted vendor name
            amount: Extracted amount
            invoice_number: Extracted invoice number
            invoice_date: Extracted date

        Returns:
            Confidence score between 0.0 and 1.0
        """
        score = 0.0

        if vendor:
            score += 0.3
        if amount > 0:
            score += 0.3
        if invoice_number:
            score += 0.2
        if invoice_date:
            score += 0.2

        return min(score, 1.0)

    def _html_to_text(self, html: str) -> str:
        """
        Convert HTML to plain text (simple version)

        For production, consider using BeautifulSoup or html2text
        """
        # Remove script and style tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)

        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        return text.strip()


# Helper function for easy access
def parse_invoice(
    content: bytes | str,
    content_type: str = "pdf"
) -> InvoiceExtractionResult:
    """
    Parse invoice from content

    Args:
        content: File bytes or text string
        content_type: "pdf", "html", or "text"

    Returns:
        InvoiceExtractionResult
    """
    parser = InvoiceParser()

    if content_type == "pdf":
        return parser.parse_pdf(content)
    elif content_type == "html":
        return parser.parse_email_html(content)
    else:
        return parser.parse_email_text(content)
