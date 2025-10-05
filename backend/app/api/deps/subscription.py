"""
Subscription and tier-based access control dependencies
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from supabase import Client

from .auth import get_current_user, get_supabase_client
from ...services.subscription_service import SubscriptionService
from ...models.subscription import (
    SubscriptionTier,
    SubscriptionInfo,
    UsageInfo,
    OrganizationWithSubscription,
)


async def get_subscription_service(supabase: Client = Depends(get_supabase_client)) -> SubscriptionService:
    """Get subscription service instance"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not configured",
        )
    return SubscriptionService(supabase)


async def get_user_organization(
    current_user: dict = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> OrganizationWithSubscription:
    """Get current user's organization with subscription info"""
    org = await subscription_service.get_or_create_organization(
        current_user["id"], current_user["email"]
    )
    return org


async def get_subscription_info(
    org: OrganizationWithSubscription = Depends(get_user_organization),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> SubscriptionInfo:
    """Get subscription information for current user's organization"""
    return await subscription_service.get_subscription_info(org.id)


async def get_usage_info(
    org: OrganizationWithSubscription = Depends(get_user_organization),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> UsageInfo:
    """Get usage information for current user's organization"""
    return await subscription_service.get_usage_info(org.id)


async def require_active_subscription(
    subscription: SubscriptionInfo = Depends(get_subscription_info),
) -> SubscriptionInfo:
    """Require active subscription (not expired or canceled)"""
    if subscription.status in ["expired", "canceled"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Subscription is not active. Please upgrade to continue.",
        )

    if subscription.status == "trial" and subscription.trial_expired:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Trial period has expired. Please upgrade to continue.",
        )

    return subscription


async def require_tier(
    min_tier: SubscriptionTier,
    subscription: SubscriptionInfo = Depends(require_active_subscription),
) -> SubscriptionInfo:
    """
    Require minimum subscription tier

    Usage:
        @router.get("/endpoint")
        async def endpoint(
            subscription: SubscriptionInfo = Depends(lambda: require_tier(SubscriptionTier.SAVER))
        ):
            ...
    """
    tier_hierarchy = {
        SubscriptionTier.FREE: 0,
        SubscriptionTier.SAVER: 1,
        SubscriptionTier.BUSINESS: 2,
        SubscriptionTier.ENTERPRISE: 3,
    }

    if tier_hierarchy.get(subscription.tier, 0) < tier_hierarchy.get(min_tier, 0):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"This feature requires {min_tier.value} tier or higher.",
        )

    return subscription


async def check_invoice_limit(
    org: OrganizationWithSubscription = Depends(get_user_organization),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> bool:
    """Check if organization can process more invoices"""
    can_process, error_msg = await subscription_service.check_can_process_invoices(org.id)

    if not can_process:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=error_msg,
        )

    return True


async def require_trial_valid(
    org: OrganizationWithSubscription = Depends(get_user_organization),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> bool:
    """Require valid trial period"""
    is_valid = await subscription_service.check_trial_status(org.id)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Trial period has expired. Please upgrade to continue.",
        )

    return True


def require_saver_tier(
    subscription: SubscriptionInfo = Depends(require_active_subscription),
) -> SubscriptionInfo:
    """Shortcut for requiring Saver tier or higher"""
    return require_tier(SubscriptionTier.SAVER, subscription)


def require_business_tier(
    subscription: SubscriptionInfo = Depends(require_active_subscription),
) -> SubscriptionInfo:
    """Shortcut for requiring Business tier or higher"""
    return require_tier(SubscriptionTier.BUSINESS, subscription)


def require_enterprise_tier(
    subscription: SubscriptionInfo = Depends(require_active_subscription),
) -> SubscriptionInfo:
    """Shortcut for requiring Enterprise tier"""
    return require_tier(SubscriptionTier.ENTERPRISE, subscription)
