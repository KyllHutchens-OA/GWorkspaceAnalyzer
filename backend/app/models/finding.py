"""
Finding Data Models
Models for detected issues (duplicates, price increases, etc.)
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class FindingType(str, Enum):
    """Types of findings/issues detected"""
    DUPLICATE = "duplicate"
    PRICE_INCREASE = "price_increase"
    UNUSED_SUBSCRIPTION = "unused_subscription"
    ANOMALY = "anomaly"


class FindingStatus(str, Enum):
    """Status of a finding"""
    PENDING = "pending"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class DuplicateType(str, Enum):
    """Type of duplicate detected"""
    EXACT = "exact"  # Same invoice number, vendor, amount
    PROBABLE = "probable"  # Same vendor, amount, close dates
    POSSIBLE = "possible"  # Same vendor, similar amount


class Finding(BaseModel):
    """
    Base finding model
    """
    type: FindingType
    title: str = ""
    description: str = ""
    amount: Decimal
    confidence_score: float = Field(ge=0.0, le=1.0)
    invoice_ids: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)


class DuplicateFinding(Finding):
    """
    Duplicate charge finding
    """
    type: FindingType = FindingType.DUPLICATE
    duplicate_type: DuplicateType
    vendor_name: str
    invoice_count: int = 2
    date_range_days: int = 0

    def __init__(self, **data):
        super().__init__(**data)
        self.title = f"Duplicate charge from {self.vendor_name}"
        self.description = self._generate_description()

    def _generate_description(self) -> str:
        if self.duplicate_type == DuplicateType.EXACT:
            return f"Same invoice charged {self.invoice_count} times (exact match)"
        elif self.duplicate_type == DuplicateType.PROBABLE:
            return f"Likely duplicate - same amount charged {self.invoice_count} times within {self.date_range_days} days"
        else:
            return f"Possible duplicate - similar charges from {self.vendor_name}"


class PriceIncreaseFinding(Finding):
    """
    Price increase finding
    """
    type: FindingType = FindingType.PRICE_INCREASE
    vendor_name: str
    old_amount: Decimal
    new_amount: Decimal
    increase_percentage: float
    old_date: date
    new_date: date

    def __init__(self, **data):
        super().__init__(**data)
        self.title = f"Price increase from {self.vendor_name}"
        self.description = self._generate_description()

    def _generate_description(self) -> str:
        return (
            f"Price increased from ${self.old_amount} to ${self.new_amount} "
            f"({self.increase_percentage:.1f}% increase)"
        )


class UnusedSubscriptionFinding(Finding):
    """
    Unused or duplicate subscription finding
    """
    type: FindingType = FindingType.UNUSED_SUBSCRIPTION
    vendor_name: str
    subscription_type: str  # "duplicate_accounts", "unused_seats", "overlapping"
    recurring_amount: Decimal
    frequency: str  # "monthly", "annual"

    def __init__(self, **data):
        super().__init__(**data)
        self.title = f"Unused subscription: {self.vendor_name}"
        self.description = self._generate_description()

    def _generate_description(self) -> str:
        if self.subscription_type == "duplicate_accounts":
            return f"Multiple {self.vendor_name} subscriptions detected - paying {self.frequency}"
        elif self.subscription_type == "unused_seats":
            return f"Paying for unused seats on {self.vendor_name}"
        else:
            return f"Overlapping service with {self.vendor_name}"
