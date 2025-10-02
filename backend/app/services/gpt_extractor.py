"""
GPT-4o Mini Invoice Extractor
Uses OpenAI's GPT-4o Mini to extract structured invoice data from text
"""
import logging
import json
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

from openai import OpenAI
from pydantic import ValidationError

from ..models import ParsedInvoice
from ..config.settings import settings

logger = logging.getLogger(__name__)


class GPTInvoiceExtractor:
    """
    Extract invoice data using GPT-4o Mini
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize GPT extractor

        Args:
            api_key: OpenAI API key (defaults to settings.OPENAI_API_KEY)
        """
        self.client = OpenAI(api_key=api_key or settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"

    def extract_invoice_data(self, text: str) -> ParsedInvoice:
        """
        Extract structured invoice data from text using GPT-4o Mini

        Args:
            text: Raw text from invoice (PDF, email, etc.)

        Returns:
            ParsedInvoice with extracted data
        """
        try:
            # Build prompt
            prompt = self._build_extraction_prompt(text)

            # Call GPT-4o Mini
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert invoice data extraction system. Extract structured data from invoices accurately."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0,  # Deterministic output
                max_tokens=500,
            )

            # Parse response
            result = json.loads(response.choices[0].message.content)

            # Convert to ParsedInvoice
            invoice = self._parse_gpt_response(result, text)

            logger.info(f"GPT extracted: {invoice.vendor_name} - ${invoice.amount}")
            return invoice

        except Exception as e:
            logger.error(f"GPT extraction failed: {e}")
            # Return minimal invoice with unknown vendor
            return ParsedInvoice(
                vendor_name="Unknown Vendor",
                amount=Decimal("0.00"),
                currency="USD",
                confidence_score=0.0,
                extraction_method="gpt_failed",
                raw_text=text[:1000],
            )

    def _build_extraction_prompt(self, text: str) -> str:
        """
        Build extraction prompt for GPT

        Args:
            text: Invoice text

        Returns:
            Formatted prompt
        """
        # Truncate very long texts to save tokens
        max_chars = 4000
        truncated_text = text[:max_chars]
        if len(text) > max_chars:
            truncated_text += "\n... [truncated]"

        prompt = f"""Extract the following information from this invoice/receipt/billing document:

INVOICE TEXT:
{truncated_text}

Extract and return a JSON object with these fields:
{{
  "vendor_name": "Company name that issued the invoice (e.g., 'Amazon Web Services', 'Stripe', 'Zoom')",
  "invoice_number": "Invoice or order number (e.g., 'INV-12345', 'AWS-001')",
  "invoice_date": "Invoice date in YYYY-MM-DD format (e.g., '2024-01-15')",
  "due_date": "Due date in YYYY-MM-DD format (e.g., '2024-02-15')",
  "total_amount": "Total amount as a number (e.g., 2499.00, 149.99)",
  "currency": "Currency code (e.g., 'USD', 'EUR')",
  "description": "Brief description of what was purchased (e.g., 'Monthly subscription', 'AWS services')",
  "is_invoice": true/false (true if this is clearly an invoice/receipt for PAYMENT, false if it's a quote/estimate/proposal)
}}

Important:
- If a field cannot be found, use null
- For amounts, extract the TOTAL or final amount due (not line items)
- For vendor_name, use the company that SENT the invoice (not the recipient)
- For dates, parse natural language dates like "January 15, 2024" to "2024-01-15"
- Return valid JSON only, no extra text
- Set "is_invoice" to FALSE if the document is:
  * A quote, quotation, or estimate
  * A proposal or pro forma invoice
  * Contains words like "QUOTE", "QUOTATION", "ESTIMATE", "PROPOSAL" in the title
  * Shows prices but no payment has been made yet
- Set "is_invoice" to TRUE only if:
  * It's clearly an invoice or receipt for a completed transaction
  * Contains words like "INVOICE", "RECEIPT", "PAID", "PAYMENT RECEIVED"
  * Shows payment has been processed
"""
        return prompt

    def _parse_gpt_response(self, result: dict, original_text: str) -> ParsedInvoice:
        """
        Convert GPT JSON response to ParsedInvoice

        Args:
            result: JSON response from GPT
            original_text: Original invoice text

        Returns:
            ParsedInvoice object
        """
        # Parse amount
        amount = Decimal("0.00")
        if result.get("total_amount"):
            try:
                amount = Decimal(str(result["total_amount"]))
            except (ValueError, TypeError, ArithmeticError):
                logger.warning(f"Invalid amount from GPT: {result.get('total_amount')}")

        # Parse dates
        invoice_date = self._parse_date(result.get("invoice_date"))
        due_date = self._parse_date(result.get("due_date"))

        # Calculate confidence score
        confidence = self._calculate_confidence(result)

        return ParsedInvoice(
            vendor_name=result.get("vendor_name") or "Unknown Vendor",
            invoice_number=result.get("invoice_number"),
            invoice_date=invoice_date,
            due_date=due_date,
            amount=amount,
            currency=result.get("currency") or "USD",
            description=result.get("description"),
            confidence_score=confidence,
            extraction_method="gpt4o_mini",
            raw_text=original_text[:5000],
        )

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """
        Parse date string to date object

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            date object or None
        """
        if not date_str:
            return None

        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            logger.warning(f"Invalid date from GPT: {date_str}")
            return None

    def _calculate_confidence(self, result: dict) -> float:
        """
        Calculate confidence score based on extracted fields

        Args:
            result: GPT extraction result

        Returns:
            Confidence score 0.0 - 1.0
        """
        # Check if GPT thinks this is an invoice
        if not result.get("is_invoice"):
            return 0.3

        score = 0.0

        # Vendor name found (30%)
        if result.get("vendor_name"):
            score += 0.3

        # Amount found (30%)
        if result.get("total_amount") and float(result.get("total_amount", 0)) > 0:
            score += 0.3

        # Invoice number found (20%)
        if result.get("invoice_number"):
            score += 0.2

        # Date found (20%)
        if result.get("invoice_date"):
            score += 0.2

        return round(score, 2)

    def is_likely_invoice(self, text: str) -> bool:
        """
        Quick check if text is likely an invoice/receipt

        Args:
            text: Text to check

        Returns:
            True if likely an invoice
        """
        # Use simpler prompt for quick classification
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You determine if text is an invoice, receipt, or billing document."
                    },
                    {
                        "role": "user",
                        "content": f"Is this an invoice, receipt, or billing document? Answer only 'yes' or 'no'.\n\n{text[:1000]}"
                    }
                ],
                temperature=0,
                max_tokens=10,
            )

            answer = response.choices[0].message.content.strip().lower()
            return "yes" in answer

        except Exception as e:
            logger.error(f"GPT classification failed: {e}")
            # Fallback to keyword check
            keywords = ["invoice", "receipt", "bill", "payment", "total", "amount due"]
            text_lower = text[:500].lower()
            return any(keyword in text_lower for keyword in keywords)
