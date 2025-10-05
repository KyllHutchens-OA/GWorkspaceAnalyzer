"""
Subscription and tier models
"""
from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class SubscriptionTier(str, Enum):
    FREE = "free"
    SAVER = "saver"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    CANCELED = "canceled"
    EXPIRED = "expired"


class TierLimits(BaseModel):
    invoice_limit_per_month: int
    gmail_accounts_limit: int
    has_daily_scans: bool
    has_api_access: bool
    has_team_dashboard: bool
    has_priority_support: bool


TIER_FEATURES = {
    SubscriptionTier.FREE: TierLimits(
        invoice_limit_per_month=0,  # Free audit only, no ongoing
        gmail_accounts_limit=1,
        has_daily_scans=False,
        has_api_access=False,
        has_team_dashboard=False,
        has_priority_support=False,
    ),
    SubscriptionTier.SAVER: TierLimits(
        invoice_limit_per_month=1000,
        gmail_accounts_limit=1,
        has_daily_scans=False,  # Weekly only
        has_api_access=False,
        has_team_dashboard=False,
        has_priority_support=False,
    ),
    SubscriptionTier.BUSINESS: TierLimits(
        invoice_limit_per_month=999999,  # Effectively unlimited
        gmail_accounts_limit=5,
        has_daily_scans=True,
        has_api_access=True,
        has_team_dashboard=True,
        has_priority_support=True,
    ),
    SubscriptionTier.ENTERPRISE: TierLimits(
        invoice_limit_per_month=999999,  # Unlimited
        gmail_accounts_limit=999999,  # Unlimited
        has_daily_scans=True,
        has_api_access=True,
        has_team_dashboard=True,
        has_priority_support=True,
    ),
}


class SubscriptionInfo(BaseModel):
    org_id: str
    tier: SubscriptionTier
    status: SubscriptionStatus
    trial_started_at: Optional[datetime] = None
    trial_ends_at: Optional[datetime] = None
    trial_hours_remaining: Optional[float] = None
    trial_expired: bool = False
    limits: TierLimits


class UsageInfo(BaseModel):
    org_id: str
    tier: SubscriptionTier
    invoice_limit: int
    invoices_used: int
    invoices_remaining: int
    usage_percentage: float
    is_approaching_limit: bool  # >= 80%
    is_at_limit: bool  # >= 95%


class OrganizationWithSubscription(BaseModel):
    id: str
    name: str
    subscription_tier: SubscriptionTier
    subscription_status: SubscriptionStatus
    trial_started_at: Optional[datetime] = None
    trial_ends_at: Optional[datetime] = None
    invoice_limit_per_month: int
    gmail_accounts_limit: int
    created_at: datetime
    updated_at: datetime
