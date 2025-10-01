"""
Invoice Data Models
Pydantic models for invoice parsing and validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
import re


class LineItem(BaseModel):
    """Single line item on an invoice"""

    description: str
    quantity: Optional[float] = None
    unit_price: Optional[Decimal] = None
    amount: Optional[Decimal] = None
    category: Optional[str] = None


class ParsedInvoice(BaseModel):
    """
    Structured invoice data extracted from email/PDF
    """

    # Vendor information
    vendor_name: str
    vendor_name_normalized: Optional[str] = None
    vendor_email: Optional[str] = None
    vendor_address: Optional[str] = None

    # Invoice identifiers
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None

    # Financial data
    amount: Decimal
    currency: str = "USD"
    tax_amount: Optional[Decimal] = None
    subtotal: Optional[Decimal] = None

    # Line items
    line_items: List[LineItem] = Field(default_factory=list)

    # Payment information
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None

    # Metadata
    confidence_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Extraction confidence (0-1)"
    )
    extraction_method: str = Field(
        default="unknown", description="pdf_parser, ocr, html, structured_data"
    )

    # Raw data
    raw_text: Optional[str] = None

    @validator("vendor_name_normalized", always=True)
    def normalize_vendor_name(cls, v, values):
        """Auto-generate normalized vendor name"""
        if v is None and "vendor_name" in values:
            vendor = values["vendor_name"]
            # Remove all non-alphanumeric characters and lowercase
            normalized = re.sub(r'[^a-zA-Z0-9]', '', vendor).lower()
            return normalized
        return v

    @validator("amount")
    def validate_amount(cls, v):
        """Ensure amount is positive"""
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat(),
        }


class InvoiceExtractionResult(BaseModel):
    """Result of invoice extraction attempt"""

    success: bool
    invoice: Optional[ParsedInvoice] = None
    error: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)

    # Extraction metadata
    processing_time_ms: Optional[int] = None
    source_type: str  # "pdf", "email_html", "email_text"


class VendorMatch(BaseModel):
    """Vendor matching result for normalization"""

    matched_name: str
    normalized_name: str
    confidence: float
    is_new_vendor: bool
    suggested_aliases: List[str] = Field(default_factory=list)
