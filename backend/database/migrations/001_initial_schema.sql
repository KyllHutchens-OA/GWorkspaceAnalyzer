-- GWorkspace Analyzer - Initial Database Schema
-- Supabase PostgreSQL Migration
-- Version: 001
-- Description: Core tables for invoice analysis and duplicate detection

-- ============================================================================
-- EXTENSIONS
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- ENUMS
-- ============================================================================
CREATE TYPE subscription_tier AS ENUM ('free', 'pro', 'enterprise');
CREATE TYPE finding_type AS ENUM ('duplicate', 'price_increase', 'unused_subscription', 'anomaly');
CREATE TYPE finding_status AS ENUM ('pending', 'resolved', 'ignored');
CREATE TYPE scan_status AS ENUM ('queued', 'processing', 'completed', 'failed');

-- ============================================================================
-- ORGANIZATIONS
-- ============================================================================
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    google_domain TEXT UNIQUE,
    subscription_tier subscription_tier DEFAULT 'free',
    trial_ends_at TIMESTAMP,
    settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_organizations_domain ON organizations(google_domain);

-- ============================================================================
-- USERS
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    org_id UUID REFERENCES organizations(id) ON DELETE SET NULL,

    -- Token stored in Supabase Vault (reference only)
    google_token_vault_id UUID,

    last_scan_at TIMESTAMP,
    scan_count INTEGER DEFAULT 0,
    preferences JSONB DEFAULT '{
        "email_digest": true,
        "alert_threshold": 1000,
        "excluded_vendors": []
    }'::jsonb,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_org ON users(org_id);
CREATE INDEX idx_users_email ON users(email);

-- ============================================================================
-- SCAN JOBS
-- ============================================================================
CREATE TABLE scan_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,

    status scan_status DEFAULT 'queued',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,

    -- Progress tracking
    total_emails INTEGER DEFAULT 0,
    processed_emails INTEGER DEFAULT 0,
    invoices_found INTEGER DEFAULT 0,

    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_scan_jobs_user ON scan_jobs(user_id, created_at DESC);
CREATE INDEX idx_scan_jobs_status ON scan_jobs(status) WHERE status IN ('queued', 'processing');

-- ============================================================================
-- INVOICES
-- ============================================================================
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    scan_job_id UUID REFERENCES scan_jobs(id) ON DELETE SET NULL,

    -- Gmail metadata
    gmail_message_id TEXT NOT NULL,
    gmail_thread_id TEXT,
    email_subject TEXT,
    email_from TEXT,
    email_date TIMESTAMP,

    -- Invoice data
    vendor_name TEXT NOT NULL,
    vendor_name_normalized TEXT, -- Lowercase, no special chars for matching
    invoice_number TEXT,
    amount DECIMAL(12,2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    invoice_date DATE NOT NULL,
    due_date DATE,

    -- Line items and raw data
    line_items JSONB DEFAULT '[]'::jsonb,
    raw_text TEXT, -- Consider moving to separate table for scale

    -- File attachments (stored in Supabase Storage)
    attachment_urls JSONB DEFAULT '[]'::jsonb, -- Array of {filename, url, type}

    -- Metadata
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    extraction_method TEXT, -- 'pdf_parser', 'ocr', 'html', 'structured_data'

    processed_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),

    -- Composite unique constraint
    UNIQUE(org_id, gmail_message_id)
);

-- Indexes for performance
CREATE INDEX idx_invoices_org_date ON invoices(org_id, invoice_date DESC);
CREATE INDEX idx_invoices_gmail_msg ON invoices(gmail_message_id);
CREATE INDEX idx_invoices_vendor ON invoices(org_id, vendor_name_normalized, invoice_date);
CREATE INDEX idx_invoices_duplicate_check ON invoices(org_id, vendor_name_normalized, amount, invoice_date);

-- GIN index for JSONB queries
CREATE INDEX idx_invoices_line_items ON invoices USING GIN(line_items);

-- ============================================================================
-- INVOICE CONTENT (Separate table for large text data)
-- ============================================================================
CREATE TABLE invoice_content (
    invoice_id UUID PRIMARY KEY REFERENCES invoices(id) ON DELETE CASCADE,
    raw_text TEXT,
    raw_html TEXT,
    extracted_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- FINDINGS
-- ============================================================================
CREATE TABLE findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,

    type finding_type NOT NULL,
    status finding_status DEFAULT 'pending',

    -- Financial impact
    amount DECIMAL(12,2) NOT NULL,
    currency TEXT DEFAULT 'USD',

    -- Related invoices (using junction table instead of array)
    primary_invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,

    -- Finding details
    title TEXT NOT NULL,
    description TEXT,
    details JSONB DEFAULT '{}'::jsonb,
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00

    -- User interaction
    resolved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    resolved_at TIMESTAMP,
    user_notes TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_findings_org_status ON findings(org_id, status, created_at DESC);
CREATE INDEX idx_findings_type ON findings(type, status);
CREATE INDEX idx_findings_amount ON findings(org_id, amount DESC) WHERE status = 'pending';

-- ============================================================================
-- FINDING INVOICES (Junction Table)
-- ============================================================================
CREATE TABLE finding_invoices (
    finding_id UUID REFERENCES findings(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
    PRIMARY KEY (finding_id, invoice_id)
);

CREATE INDEX idx_finding_invoices_invoice ON finding_invoices(invoice_id);

-- ============================================================================
-- VENDOR TRACKING
-- ============================================================================
CREATE TABLE vendors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    name_normalized TEXT NOT NULL,
    aliases TEXT[] DEFAULT '{}', -- Known variations of vendor name

    -- Aggregated data
    first_seen DATE,
    last_seen DATE,
    total_invoices INTEGER DEFAULT 0,
    total_spent DECIMAL(12,2) DEFAULT 0,
    avg_invoice_amount DECIMAL(12,2),

    -- Subscription detection
    is_subscription BOOLEAN DEFAULT false,
    billing_frequency TEXT, -- 'monthly', 'quarterly', 'annual', 'one-time'

    -- User preferences
    is_excluded BOOLEAN DEFAULT false,
    notes TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(org_id, name_normalized)
);

CREATE INDEX idx_vendors_org ON vendors(org_id, last_seen DESC);
CREATE INDEX idx_vendors_subscription ON vendors(org_id, is_subscription) WHERE is_subscription = true;

-- ============================================================================
-- AUDIT LOG
-- ============================================================================
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,

    action TEXT NOT NULL, -- 'finding_resolved', 'finding_ignored', 'vendor_excluded', etc.
    entity_type TEXT, -- 'finding', 'invoice', 'vendor'
    entity_id UUID,

    changes JSONB, -- Before/after values
    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_log_org ON audit_log(org_id, created_at DESC);
CREATE INDEX idx_audit_log_user ON audit_log(user_id, created_at DESC);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Organizations
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own organization"
    ON organizations FOR SELECT
    USING (id IN (SELECT org_id FROM users WHERE users.id = auth.uid()));

CREATE POLICY "Users can update their own organization"
    ON organizations FOR UPDATE
    USING (id IN (SELECT org_id FROM users WHERE users.id = auth.uid()));

-- Users
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own data"
    ON users FOR SELECT
    USING (id = auth.uid());

CREATE POLICY "Users can update their own data"
    ON users FOR UPDATE
    USING (id = auth.uid());

-- Invoices
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their org's invoices"
    ON invoices FOR SELECT
    USING (org_id IN (SELECT org_id FROM users WHERE users.id = auth.uid()));

CREATE POLICY "Users can insert invoices to their org"
    ON invoices FOR INSERT
    WITH CHECK (org_id IN (SELECT org_id FROM users WHERE users.id = auth.uid()));

-- Findings
ALTER TABLE findings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their org's findings"
    ON findings FOR SELECT
    USING (org_id IN (SELECT org_id FROM users WHERE users.id = auth.uid()));

CREATE POLICY "Users can update their org's findings"
    ON findings FOR UPDATE
    USING (org_id IN (SELECT org_id FROM users WHERE users.id = auth.uid()));

-- Scan Jobs
ALTER TABLE scan_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own scan jobs"
    ON scan_jobs FOR SELECT
    USING (user_id = auth.uid());

-- Vendors
ALTER TABLE vendors ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their org's vendors"
    ON vendors FOR SELECT
    USING (org_id IN (SELECT org_id FROM users WHERE users.id = auth.uid()));

CREATE POLICY "Users can update their org's vendors"
    ON vendors FOR UPDATE
    USING (org_id IN (SELECT org_id FROM users WHERE users.id = auth.uid()));

-- Audit Log
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their org's audit log"
    ON audit_log FOR SELECT
    USING (org_id IN (SELECT org_id FROM users WHERE users.id = auth.uid()));

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER findings_updated_at
    BEFORE UPDATE ON findings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER vendors_updated_at
    BEFORE UPDATE ON vendors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Auto-generate normalized vendor name
CREATE OR REPLACE FUNCTION normalize_vendor_name()
RETURNS TRIGGER AS $$
BEGIN
    NEW.vendor_name_normalized = LOWER(REGEXP_REPLACE(NEW.vendor_name, '[^a-zA-Z0-9]', '', 'g'));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER invoices_normalize_vendor
    BEFORE INSERT OR UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION normalize_vendor_name();

CREATE TRIGGER vendors_normalize_name
    BEFORE INSERT OR UPDATE ON vendors
    FOR EACH ROW
    WHEN (NEW.name IS NOT NULL)
    EXECUTE FUNCTION normalize_vendor_name();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Dashboard summary view
CREATE VIEW dashboard_summary AS
SELECT
    f.org_id,
    COUNT(*) FILTER (WHERE f.status = 'pending') as pending_findings,
    COUNT(*) FILTER (WHERE f.type = 'duplicate') as duplicate_count,
    COUNT(*) FILTER (WHERE f.type = 'price_increase') as price_increase_count,
    COUNT(*) FILTER (WHERE f.type = 'unused_subscription') as unused_subscription_count,
    COALESCE(SUM(f.amount) FILTER (WHERE f.status = 'pending'), 0) as total_waste,
    COALESCE(SUM(f.amount) FILTER (WHERE f.type = 'duplicate' AND f.status = 'pending'), 0) as duplicate_waste,
    COALESCE(SUM(f.amount) FILTER (WHERE f.type = 'price_increase' AND f.status = 'pending'), 0) as price_increase_waste,
    COALESCE(SUM(f.amount) FILTER (WHERE f.type = 'unused_subscription' AND f.status = 'pending'), 0) as subscription_waste
FROM findings f
GROUP BY f.org_id;

-- Recent invoices view
CREATE VIEW recent_invoices AS
SELECT
    i.id,
    i.org_id,
    i.vendor_name,
    i.amount,
    i.currency,
    i.invoice_date,
    i.invoice_number,
    i.gmail_message_id,
    v.is_subscription,
    v.billing_frequency
FROM invoices i
LEFT JOIN vendors v ON v.org_id = i.org_id AND v.name_normalized = i.vendor_name_normalized
ORDER BY i.invoice_date DESC;

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert sample subscription tier if needed for testing
-- (Remove in production)

COMMENT ON TABLE organizations IS 'Business organizations using the app';
COMMENT ON TABLE users IS 'Individual users linked to Supabase Auth';
COMMENT ON TABLE invoices IS 'Parsed invoice data from Gmail';
COMMENT ON TABLE findings IS 'Detected issues: duplicates, price increases, etc.';
COMMENT ON TABLE vendors IS 'Aggregated vendor tracking and subscription detection';
COMMENT ON TABLE scan_jobs IS 'Gmail scanning job tracking';
COMMENT ON TABLE audit_log IS 'User action history for compliance';
