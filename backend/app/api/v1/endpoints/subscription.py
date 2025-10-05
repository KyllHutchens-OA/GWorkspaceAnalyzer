"""
Subscription management endpoints
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ....models.subscription import (
    SubscriptionInfo,
    UsageInfo,
    SubscriptionTier,
    OrganizationWithSubscription,
)
from ....services.subscription_service import SubscriptionService
from ...deps.subscription import (
    get_subscription_info,
    get_usage_info,
    get_user_organization,
    get_subscription_service,
)
from ...deps.auth import get_current_user

router = APIRouter()


class UpgradeRequest(BaseModel):
    tier: SubscriptionTier


class SubscriptionStatusResponse(BaseModel):
    subscription: SubscriptionInfo
    usage: UsageInfo
    organization: OrganizationWithSubscription


@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    subscription: SubscriptionInfo = Depends(get_subscription_info),
    usage: UsageInfo = Depends(get_usage_info),
    org: OrganizationWithSubscription = Depends(get_user_organization),
) -> SubscriptionStatusResponse:
    """
    Get current subscription status, usage, and organization info
    """
    return SubscriptionStatusResponse(
        subscription=subscription,
        usage=usage,
        organization=org,
    )


@router.get("/trial/status")
async def get_trial_status(
    subscription: SubscriptionInfo = Depends(get_subscription_info),
) -> Dict[str, Any]:
    """
    Get trial status information
    """
    if subscription.status != "trial":
        return {
            "is_trial": False,
            "message": "Not on trial"
        }

    return {
        "is_trial": True,
        "trial_started_at": subscription.trial_started_at,
        "trial_ends_at": subscription.trial_ends_at,
        "hours_remaining": subscription.trial_hours_remaining,
        "is_expired": subscription.trial_expired,
    }


@router.post("/trial/start")
async def start_trial(
    org: OrganizationWithSubscription = Depends(get_user_organization),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Start 48-hour trial period
    """
    # Check if already on trial or has active subscription
    subscription = await subscription_service.get_subscription_info(org.id)

    if subscription.status == "trial":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trial already active"
        )

    if subscription.status == "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already have active subscription"
        )

    updated_org = await subscription_service.start_trial(org.id)

    return {
        "success": True,
        "message": "Trial started",
        "trial_ends_at": updated_org.trial_ends_at,
    }


@router.post("/upgrade")
async def upgrade_subscription(
    request: UpgradeRequest,
    org: OrganizationWithSubscription = Depends(get_user_organization),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Upgrade subscription tier

    Note: This is a simplified version. In production, this would integrate with Stripe
    to handle payment before upgrading.
    """
    current_subscription = await subscription_service.get_subscription_info(org.id)

    # Validate upgrade path
    tier_hierarchy = {
        SubscriptionTier.FREE: 0,
        SubscriptionTier.SAVER: 1,
        SubscriptionTier.BUSINESS: 2,
        SubscriptionTier.ENTERPRISE: 3,
    }

    if tier_hierarchy.get(request.tier, 0) <= tier_hierarchy.get(current_subscription.tier, 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only upgrade to higher tier"
        )

    # In production, this would:
    # 1. Create Stripe checkout session
    # 2. Redirect user to Stripe
    # 3. Handle webhook to confirm payment
    # 4. Then upgrade tier

    # For now, just upgrade directly (testing only)
    updated_org = await subscription_service.upgrade_tier(org.id, request.tier)

    return {
        "success": True,
        "message": f"Upgraded to {request.tier.value}",
        "organization": updated_org.dict(),
    }


@router.get("/usage")
async def get_usage(
    usage: UsageInfo = Depends(get_usage_info),
) -> UsageInfo:
    """
    Get current usage information
    """
    return usage


@router.get("/limits")
async def get_subscription_limits(
    subscription: SubscriptionInfo = Depends(get_subscription_info),
) -> Dict[str, Any]:
    """
    Get subscription tier limits and features
    """
    return {
        "tier": subscription.tier,
        "limits": subscription.limits.dict(),
    }


@router.get("/features")
async def get_available_features(
    subscription: SubscriptionInfo = Depends(get_subscription_info),
) -> Dict[str, Any]:
    """
    Get list of features available for current tier
    """
    limits = subscription.limits

    return {
        "tier": subscription.tier,
        "features": {
            "invoice_processing": {
                "enabled": True,
                "limit_per_month": limits.invoice_limit_per_month,
                "is_unlimited": limits.invoice_limit_per_month >= 999999,
            },
            "gmail_accounts": {
                "enabled": True,
                "limit": limits.gmail_accounts_limit,
                "is_unlimited": limits.gmail_accounts_limit >= 999999,
            },
            "daily_scans": {
                "enabled": limits.has_daily_scans,
            },
            "api_access": {
                "enabled": limits.has_api_access,
            },
            "team_dashboard": {
                "enabled": limits.has_team_dashboard,
            },
            "priority_support": {
                "enabled": limits.has_priority_support,
            },
        },
    }


@router.get("/pricing")
async def get_pricing_tiers() -> Dict[str, Any]:
    """
    Get pricing information for all tiers
    """
    return {
        "tiers": [
            {
                "id": "free",
                "name": "Free Audit",
                "price": 0,
                "billing_period": "one-time",
                "description": "90-day scan with 48-hour dashboard access",
                "features": [
                    "Complete 90-day Gmail scan",
                    "Full waste report",
                    "48-hour dashboard access",
                    "No credit card required",
                ],
                "limits": {
                    "invoice_limit": 0,
                    "gmail_accounts": 1,
                },
            },
            {
                "id": "saver",
                "name": "Saver",
                "price": 49,
                "billing_period": "monthly",
                "description": "Perfect for individuals and small businesses",
                "features": [
                    "1 Gmail account monitored",
                    "Weekly automated scans",
                    "Up to 1,000 invoices/month",
                    "Real-time duplicate detection",
                    "Email notifications",
                    "Export reports (PDF/CSV)",
                    "ROI tracking dashboard",
                ],
                "limits": {
                    "invoice_limit": 1000,
                    "gmail_accounts": 1,
                },
                "roi": "65:1",
                "guarantee": "$500 savings in 30 days or refund + $100",
            },
            {
                "id": "business",
                "name": "Business",
                "price": 297,
                "billing_period": "monthly",
                "description": "For teams that need more power",
                "features": [
                    "Up to 5 Gmail accounts",
                    "Daily automated scans",
                    "Unlimited invoice processing",
                    "Team dashboard (5 users)",
                    "Priority support (24h response)",
                    "API access (read-only)",
                    "Custom alert thresholds",
                    "Monthly executive reports",
                ],
                "limits": {
                    "invoice_limit": 999999,
                    "gmail_accounts": 5,
                },
                "roi": "28:1",
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price": 997,
                "billing_period": "monthly",
                "description": "Custom solution for large organizations",
                "features": [
                    "Unlimited Gmail accounts",
                    "Real-time continuous monitoring",
                    "Full API access with webhooks",
                    "Custom integrations",
                    "Dedicated account manager",
                    "Quarterly business reviews",
                    "SSO/SAML integration",
                    "Custom features on request",
                ],
                "limits": {
                    "invoice_limit": 999999,
                    "gmail_accounts": 999999,
                },
                "roi": "50:1 to 500:1",
                "contact_sales": True,
            },
        ],
    }
