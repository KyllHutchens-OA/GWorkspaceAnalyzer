"""
Subscription management service
"""
from typing import Optional, Tuple
from datetime import datetime, timedelta
from supabase import Client

from ..models.subscription import (
    SubscriptionTier,
    SubscriptionStatus,
    SubscriptionInfo,
    UsageInfo,
    TIER_FEATURES,
    OrganizationWithSubscription,
)


class SubscriptionService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def get_or_create_organization(self, user_id: str, user_email: str) -> OrganizationWithSubscription:
        """Get or create organization for user"""
        # Check if user has org
        user_result = self.supabase.table("users").select("*, organizations(*)").eq("id", user_id).execute()

        if not user_result.data or len(user_result.data) == 0:
            raise ValueError("User not found")

        user_data = user_result.data[0]

        # If user has org, return it
        if user_data.get("org_id") and user_data.get("organizations"):
            org = user_data["organizations"]
            return OrganizationWithSubscription(**org)

        # Create new organization
        org_name = user_email.split("@")[0] + "'s Organization"
        trial_started_at = datetime.utcnow()
        trial_ends_at = trial_started_at + timedelta(hours=48)

        new_org = {
            "name": org_name,
            "subscription_tier": SubscriptionTier.FREE.value,
            "subscription_status": SubscriptionStatus.TRIAL.value,
            "trial_started_at": trial_started_at.isoformat(),
            "trial_ends_at": trial_ends_at.isoformat(),
            "invoice_limit_per_month": 0,  # Free tier
            "gmail_accounts_limit": 1,
        }

        org_result = self.supabase.table("organizations").insert(new_org).execute()

        if not org_result.data or len(org_result.data) == 0:
            raise ValueError("Failed to create organization")

        org = org_result.data[0]

        # Link user to org
        self.supabase.table("users").update({"org_id": org["id"]}).eq("id", user_id).execute()

        return OrganizationWithSubscription(**org)

    async def get_subscription_info(self, org_id: str) -> SubscriptionInfo:
        """Get subscription information for organization"""
        result = self.supabase.rpc("subscription_info", {}).execute()

        # Find the org in results
        org_info = None
        if result.data:
            org_info = next((item for item in result.data if item["org_id"] == org_id), None)

        if not org_info:
            # Fallback to direct query
            org_result = self.supabase.table("organizations").select("*").eq("id", org_id).execute()

            if not org_result.data or len(org_result.data) == 0:
                raise ValueError("Organization not found")

            org = org_result.data[0]
            org_info = {
                "org_id": org["id"],
                "subscription_tier": org["subscription_tier"],
                "subscription_status": org["subscription_status"],
                "trial_started_at": org.get("trial_started_at"),
                "trial_ends_at": org.get("trial_ends_at"),
                "trial_hours_remaining": None,
                "trial_expired": False,
                "invoice_limit_per_month": org["invoice_limit_per_month"],
                "gmail_accounts_limit": org["gmail_accounts_limit"],
            }

            # Calculate trial hours remaining
            if org_info["subscription_status"] == "trial" and org_info["trial_ends_at"]:
                trial_end = datetime.fromisoformat(org_info["trial_ends_at"].replace("Z", "+00:00"))
                hours_remaining = (trial_end - datetime.utcnow()).total_seconds() / 3600
                org_info["trial_hours_remaining"] = max(0, hours_remaining)
                org_info["trial_expired"] = hours_remaining <= 0

        tier = SubscriptionTier(org_info["subscription_tier"])
        limits = TIER_FEATURES[tier]

        return SubscriptionInfo(
            org_id=org_info["org_id"],
            tier=tier,
            status=SubscriptionStatus(org_info["subscription_status"]),
            trial_started_at=org_info.get("trial_started_at"),
            trial_ends_at=org_info.get("trial_ends_at"),
            trial_hours_remaining=org_info.get("trial_hours_remaining"),
            trial_expired=org_info.get("trial_expired", False),
            limits=limits,
        )

    async def get_usage_info(self, org_id: str) -> UsageInfo:
        """Get current month usage information"""
        result = self.supabase.rpc("current_month_usage", {}).execute()

        # Find the org in results
        usage_data = None
        if result.data:
            usage_data = next((item for item in result.data if item["org_id"] == org_id), None)

        if not usage_data:
            # Fallback: get org tier and check usage_tracking
            org_result = self.supabase.table("organizations").select("*").eq("id", org_id).execute()

            if not org_result.data:
                raise ValueError("Organization not found")

            org = org_result.data[0]

            # Get current month usage
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            usage_result = (
                self.supabase.table("usage_tracking")
                .select("*")
                .eq("org_id", org_id)
                .eq("period_start", current_month_start.date().isoformat())
                .execute()
            )

            invoices_used = 0
            if usage_result.data and len(usage_result.data) > 0:
                invoices_used = usage_result.data[0].get("invoices_processed", 0)

            invoice_limit = org["invoice_limit_per_month"]
            invoices_remaining = max(0, invoice_limit - invoices_used)

            # Calculate percentage
            if invoice_limit == 0:
                usage_percentage = 0
            elif invoice_limit >= 999999:  # Unlimited
                usage_percentage = 0
            else:
                usage_percentage = round((invoices_used / invoice_limit) * 100, 2)

            usage_data = {
                "org_id": org_id,
                "subscription_tier": org["subscription_tier"],
                "invoice_limit_per_month": invoice_limit,
                "invoices_used": invoices_used,
                "invoices_remaining": invoices_remaining,
                "usage_percentage": usage_percentage,
            }

        tier = SubscriptionTier(usage_data["subscription_tier"])

        return UsageInfo(
            org_id=usage_data["org_id"],
            tier=tier,
            invoice_limit=usage_data["invoice_limit_per_month"],
            invoices_used=usage_data["invoices_used"],
            invoices_remaining=usage_data["invoices_remaining"],
            usage_percentage=usage_data["usage_percentage"],
            is_approaching_limit=usage_data["usage_percentage"] >= 80,
            is_at_limit=usage_data["usage_percentage"] >= 95,
        )

    async def check_can_process_invoices(self, org_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if organization can process more invoices

        Returns:
            Tuple of (can_process, error_message)
        """
        subscription = await self.get_subscription_info(org_id)

        # Check if trial expired
        if subscription.status == SubscriptionStatus.TRIAL and subscription.trial_expired:
            return False, "Trial period has expired. Please upgrade to continue."

        # Check if subscription is active
        if subscription.status in [SubscriptionStatus.CANCELED, SubscriptionStatus.EXPIRED]:
            return False, "Subscription is not active. Please renew to continue."

        # Check usage limits
        usage = await self.get_usage_info(org_id)

        # Enterprise and Business have unlimited
        if subscription.tier in [SubscriptionTier.ENTERPRISE, SubscriptionTier.BUSINESS]:
            return True, None

        # Check if at limit
        if usage.invoices_used >= usage.invoice_limit:
            return False, f"Monthly invoice limit reached ({usage.invoice_limit}). Upgrade to process more."

        return True, None

    async def check_trial_status(self, org_id: str) -> bool:
        """Check if trial is still valid"""
        subscription = await self.get_subscription_info(org_id)

        if subscription.status != SubscriptionStatus.TRIAL:
            return True  # Not on trial, access granted

        if subscription.trial_expired:
            # Update status to expired
            self.supabase.table("organizations").update(
                {"subscription_status": SubscriptionStatus.EXPIRED.value}
            ).eq("id", org_id).execute()
            return False

        return True

    async def start_trial(self, org_id: str) -> OrganizationWithSubscription:
        """Start 48-hour trial for organization"""
        trial_started_at = datetime.utcnow()
        trial_ends_at = trial_started_at + timedelta(hours=48)

        update_data = {
            "subscription_status": SubscriptionStatus.TRIAL.value,
            "trial_started_at": trial_started_at.isoformat(),
            "trial_ends_at": trial_ends_at.isoformat(),
        }

        result = self.supabase.table("organizations").update(update_data).eq("id", org_id).execute()

        if not result.data or len(result.data) == 0:
            raise ValueError("Failed to start trial")

        return OrganizationWithSubscription(**result.data[0])

    async def upgrade_tier(self, org_id: str, new_tier: SubscriptionTier) -> OrganizationWithSubscription:
        """Upgrade organization to new tier"""
        limits = TIER_FEATURES[new_tier]

        update_data = {
            "subscription_tier": new_tier.value,
            "subscription_status": SubscriptionStatus.ACTIVE.value,
            "invoice_limit_per_month": limits.invoice_limit_per_month,
            "gmail_accounts_limit": limits.gmail_accounts_limit,
        }

        result = self.supabase.table("organizations").update(update_data).eq("id", org_id).execute()

        if not result.data or len(result.data) == 0:
            raise ValueError("Failed to upgrade tier")

        return OrganizationWithSubscription(**result.data[0])
