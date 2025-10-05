-- GWorkspace Analyzer - Subscription Tiers Migration
-- Supabase PostgreSQL Migration
-- Version: 002
-- Description: Add subscription tier system with usage limits and trial management

-- ============================================================================
-- UPDATE SUBSCRIPTION TIER ENUM
-- ============================================================================

-- Rename old enum
ALTER TYPE subscription_tier RENAME TO subscription_tier_old;

-- Create new enum with updated tiers
CREATE TYPE subscription_tier AS ENUM ('free', 'saver', 'business', 'enterprise');

-- Update organizations table to use new enum
ALTER TABLE organizations
    ALTER COLUMN subscription_tier DROP DEFAULT,
    ALTER COLUMN subscription_tier TYPE subscription_tier
        USING CASE subscription_tier_old::text
            WHEN 'pro' THEN 'saver'::subscription_tier
            ELSE subscription_tier_old::text::subscription_tier
        END,
    ALTER COLUMN subscription_tier SET DEFAULT 'free';

-- Drop old enum
DROP TYPE subscription_tier_old;

-- ============================================================================
-- ADD SUBSCRIPTION STATUS ENUM
-- ============================================================================

CREATE TYPE subscription_status AS ENUM ('trial', 'active', 'canceled', 'expired');

-- ============================================================================
-- UPDATE ORGANIZATIONS TABLE
-- ============================================================================

ALTER TABLE organizations
    -- Subscription status
    ADD COLUMN subscription_status subscription_status DEFAULT 'trial',

    -- Trial management
    ADD COLUMN trial_started_at TIMESTAMP,

    -- Usage limits per tier
    ADD COLUMN invoice_limit_per_month INTEGER DEFAULT 1000,
    ADD COLUMN gmail_accounts_limit INTEGER DEFAULT 1,

    -- Stripe integration (for future use)
    ADD COLUMN stripe_customer_id TEXT UNIQUE,
    ADD COLUMN stripe_subscription_id TEXT UNIQUE;

-- Set trial_started_at for existing orgs if trial_ends_at exists
UPDATE organizations
SET trial_started_at = trial_ends_at - INTERVAL '48 hours'
WHERE trial_ends_at IS NOT NULL AND trial_started_at IS NULL;

-- Create index for subscription queries
CREATE INDEX idx_organizations_subscription ON organizations(subscription_tier, subscription_status);
CREATE INDEX idx_organizations_trial_expires ON organizations(trial_ends_at)
    WHERE subscription_status = 'trial' AND trial_ends_at IS NOT NULL;

-- ============================================================================
-- CREATE USAGE TRACKING TABLE
-- ============================================================================

CREATE TABLE usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,

    -- Time period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- Usage metrics
    invoices_processed INTEGER DEFAULT 0,
    scans_performed INTEGER DEFAULT 0,
    gmail_accounts_connected INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Ensure one record per org per period
    UNIQUE(org_id, period_start)
);

CREATE INDEX idx_usage_tracking_org_period ON usage_tracking(org_id, period_start DESC);

-- ============================================================================
-- UPDATE USERS TABLE
-- ============================================================================

-- Add trial start tracking to users
ALTER TABLE users
    ADD COLUMN trial_started_at TIMESTAMP,
    ADD COLUMN subscription_tier subscription_tier DEFAULT 'free',
    ADD COLUMN subscription_status subscription_status DEFAULT 'trial';

-- ============================================================================
-- FUNCTIONS FOR SUBSCRIPTION MANAGEMENT
-- ============================================================================

-- Function to check if org is within invoice limit
CREATE OR REPLACE FUNCTION check_invoice_limit(org_uuid UUID)
RETURNS BOOLEAN AS $$
DECLARE
    org_tier subscription_tier;
    org_limit INTEGER;
    current_usage INTEGER;
    current_month_start DATE;
BEGIN
    -- Get org tier and limit
    SELECT subscription_tier, invoice_limit_per_month
    INTO org_tier, org_limit
    FROM organizations
    WHERE id = org_uuid;

    -- Enterprise and active business get unlimited
    IF org_tier IN ('enterprise', 'business') THEN
        RETURN TRUE;
    END IF;

    -- Calculate current month start
    current_month_start := DATE_TRUNC('month', CURRENT_DATE);

    -- Get current month's usage
    SELECT COALESCE(invoices_processed, 0)
    INTO current_usage
    FROM usage_tracking
    WHERE org_id = org_uuid
        AND period_start = current_month_start;

    -- Check if within limit
    RETURN current_usage < org_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to check if trial is expired
CREATE OR REPLACE FUNCTION is_trial_expired(org_uuid UUID)
RETURNS BOOLEAN AS $$
DECLARE
    trial_end TIMESTAMP;
    sub_status subscription_status;
BEGIN
    SELECT trial_ends_at, subscription_status
    INTO trial_end, sub_status
    FROM organizations
    WHERE id = org_uuid;

    -- If not on trial, return false
    IF sub_status != 'trial' THEN
        RETURN FALSE;
    END IF;

    -- Check if trial_ends_at is in the past
    RETURN trial_end IS NOT NULL AND trial_end < NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to get remaining trial time in hours
CREATE OR REPLACE FUNCTION get_trial_hours_remaining(org_uuid UUID)
RETURNS NUMERIC AS $$
DECLARE
    trial_end TIMESTAMP;
    sub_status subscription_status;
    hours_remaining NUMERIC;
BEGIN
    SELECT trial_ends_at, subscription_status
    INTO trial_end, sub_status
    FROM organizations
    WHERE id = org_uuid;

    -- If not on trial, return null
    IF sub_status != 'trial' OR trial_end IS NULL THEN
        RETURN NULL;
    END IF;

    -- Calculate hours remaining
    hours_remaining := EXTRACT(EPOCH FROM (trial_end - NOW())) / 3600;

    -- Return 0 if negative
    IF hours_remaining < 0 THEN
        RETURN 0;
    END IF;

    RETURN hours_remaining;
END;
$$ LANGUAGE plpgsql;

-- Function to increment invoice usage
CREATE OR REPLACE FUNCTION increment_invoice_usage(org_uuid UUID)
RETURNS VOID AS $$
DECLARE
    current_month_start DATE;
BEGIN
    current_month_start := DATE_TRUNC('month', CURRENT_DATE);

    -- Insert or update usage tracking
    INSERT INTO usage_tracking (org_id, period_start, period_end, invoices_processed)
    VALUES (
        org_uuid,
        current_month_start,
        (current_month_start + INTERVAL '1 month' - INTERVAL '1 day')::DATE,
        1
    )
    ON CONFLICT (org_id, period_start)
    DO UPDATE SET
        invoices_processed = usage_tracking.invoices_processed + 1,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Auto-update usage tracking on invoice insert
CREATE OR REPLACE FUNCTION auto_track_invoice_usage()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM increment_invoice_usage(NEW.org_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER track_invoice_usage
    AFTER INSERT ON invoices
    FOR EACH ROW
    EXECUTE FUNCTION auto_track_invoice_usage();

-- Updated_at trigger for usage_tracking
CREATE TRIGGER usage_tracking_updated_at
    BEFORE UPDATE ON usage_tracking
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- ROW LEVEL SECURITY FOR NEW TABLES
-- ============================================================================

ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their org's usage tracking"
    ON usage_tracking FOR SELECT
    USING (org_id IN (SELECT org_id FROM users WHERE users.id = auth.uid()));

-- ============================================================================
-- HELPER VIEWS
-- ============================================================================

-- View for current month usage
CREATE VIEW current_month_usage AS
SELECT
    u.org_id,
    o.subscription_tier,
    o.invoice_limit_per_month,
    COALESCE(u.invoices_processed, 0) as invoices_used,
    o.invoice_limit_per_month - COALESCE(u.invoices_processed, 0) as invoices_remaining,
    CASE
        WHEN o.subscription_tier IN ('enterprise', 'business') THEN 100
        WHEN o.invoice_limit_per_month = 0 THEN 0
        ELSE ROUND((COALESCE(u.invoices_processed, 0)::NUMERIC / o.invoice_limit_per_month) * 100, 2)
    END as usage_percentage
FROM organizations o
LEFT JOIN usage_tracking u ON u.org_id = o.id
    AND u.period_start = DATE_TRUNC('month', CURRENT_DATE)::DATE;

-- View for subscription status with trial info
CREATE VIEW subscription_info AS
SELECT
    o.id as org_id,
    o.subscription_tier,
    o.subscription_status,
    o.trial_started_at,
    o.trial_ends_at,
    CASE
        WHEN o.subscription_status = 'trial' AND o.trial_ends_at IS NOT NULL THEN
            EXTRACT(EPOCH FROM (o.trial_ends_at - NOW())) / 3600
        ELSE NULL
    END as trial_hours_remaining,
    CASE
        WHEN o.subscription_status = 'trial' AND o.trial_ends_at < NOW() THEN TRUE
        ELSE FALSE
    END as trial_expired,
    o.invoice_limit_per_month,
    o.gmail_accounts_limit
FROM organizations o;

-- ============================================================================
-- SET DEFAULT TIER LIMITS
-- ============================================================================

-- Update existing free tier orgs with default limits
UPDATE organizations
SET
    invoice_limit_per_month = CASE subscription_tier
        WHEN 'free' THEN 0  -- Free audit only, no ongoing processing
        WHEN 'saver' THEN 1000
        WHEN 'business' THEN 999999  -- Effectively unlimited
        WHEN 'enterprise' THEN 999999  -- Effectively unlimited
    END,
    gmail_accounts_limit = CASE subscription_tier
        WHEN 'free' THEN 1
        WHEN 'saver' THEN 1
        WHEN 'business' THEN 5
        WHEN 'enterprise' THEN 999999  -- Effectively unlimited
    END
WHERE invoice_limit_per_month IS NULL OR gmail_accounts_limit IS NULL;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE usage_tracking IS 'Tracks monthly usage metrics per organization for tier enforcement';
COMMENT ON FUNCTION check_invoice_limit IS 'Returns true if org is within their invoice processing limit for current month';
COMMENT ON FUNCTION is_trial_expired IS 'Returns true if organization trial period has expired';
COMMENT ON FUNCTION get_trial_hours_remaining IS 'Returns hours remaining in trial, 0 if expired, NULL if not on trial';
COMMENT ON VIEW current_month_usage IS 'Current month invoice usage stats per organization';
COMMENT ON VIEW subscription_info IS 'Subscription and trial status information per organization';
