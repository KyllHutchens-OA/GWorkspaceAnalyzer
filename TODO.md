# GWorkspace Analyzer - Development Tasks

## Current Status: Core MVP Complete ✅

### Completed Features
- ✅ Gmail OAuth + API integration
- ✅ Invoice PDF parsing and extraction
- ✅ Duplicate detection (exact + probable)
- ✅ Price increase monitoring
- ✅ Subscription sprawl detection
- ✅ Background scan job processing
- ✅ Real-time scan progress tracking
- ✅ Dashboard with live data
- ✅ Finding details and filtering
- ✅ CSV export functionality
- ✅ Activity logging
- ✅ Supabase authentication

---

## HIGH PRIORITY - New Pricing Model Implementation

### Pricing Tiers (Updated Model)

**FREE AUDIT** - One-Time Scan
- 90-day Gmail scan
- Full waste report
- 48-hour dashboard access
- No credit card required

**SAVER** - $49/month
- 1 Gmail account
- Weekly automated scans
- Up to 1,000 invoices/month
- Real-time duplicate detection
- Email + Slack notifications
- Export reports (PDF/CSV)

**BUSINESS** - $297/month
- Up to 5 Gmail accounts
- Daily automated scans
- Unlimited invoice processing
- Team dashboard (5 users)
- Priority support (24h response)
- API access (read-only)
- Custom alert thresholds

**ENTERPRISE** - Starting at $997/month
- Unlimited Gmail accounts
- Real-time continuous monitoring
- Full API access with webhooks
- Custom integrations
- Dedicated account manager
- Features on request

### Backend Tasks - Pricing Implementation

#### 1. Database Schema Updates
- [ ] Add `subscription_tier` enum to users table ('free', 'saver', 'business', 'enterprise')
- [ ] Add `subscription_status` field ('trial', 'active', 'canceled', 'expired')
- [ ] Add `trial_started_at` timestamp
- [ ] Add `trial_expires_at` timestamp (48 hours from start)
- [ ] Add `invoice_limit_per_month` integer field
- [ ] Add `gmail_accounts_limit` integer field
- [ ] Create `subscriptions` table with Stripe subscription ID
- [ ] Create `usage_tracking` table for invoice counts per month

#### 2. Access Control & Limits
- [ ] Implement tier-based access control middleware
- [ ] Add invoice processing limit checks (1,000/month for Saver)
- [ ] Add Gmail account limit enforcement (1 for Saver, 5 for Business)
- [ ] Implement 48-hour trial timer for Free Audit
- [ ] Create automatic trial expiration job
- [ ] Add scan frequency limits (weekly automated for Saver, daily for Business)

#### 3. Stripe Integration
- [ ] Set up Stripe account and API keys
- [ ] Create Stripe product and price objects for each tier
- [ ] Implement checkout session creation endpoint
- [ ] Build webhook handler for subscription events
- [ ] Add subscription creation/update logic
- [ ] Implement subscription cancellation flow
- [ ] Add payment method management endpoints

#### 4. Feature Gating APIs
- [ ] Create `/api/v1/subscription/status` endpoint
- [ ] Create `/api/v1/subscription/upgrade` endpoint
- [ ] Add tier check to scan job creation
- [ ] Add tier check to invoice processing
- [ ] Implement usage tracking endpoint
- [ ] Create billing portal redirect endpoint

### Frontend Tasks - Pricing Implementation

#### 5. Trial Experience
- [ ] Create 48-hour countdown timer component
- [ ] Add trial expiration banner to dashboard
- [ ] Build "Trial Expired" paywall modal
- [ ] Implement urgency messaging ("Dashboard access expires in X hours")
- [ ] Add value proposition display ("You're wasting $X, save it for $49/month")

#### 6. Upgrade Flow UI
- [ ] Create pricing comparison page/modal
- [ ] Build Stripe checkout integration
- [ ] Add "Upgrade Now" CTAs throughout dashboard
- [ ] Implement tier badge display (Free/Saver/Business/Enterprise)
- [ ] Create usage limit warnings (e.g., "800/1,000 invoices used")
- [ ] Build upgrade triggers (approaching limits, multiple accounts, etc.)

#### 7. Subscription Management
- [ ] Create subscription settings page
- [ ] Add billing history display
- [ ] Implement payment method update flow
- [ ] Build cancel subscription flow with retention offers
- [ ] Add invoice download for payments

#### 8. Feature Access Control
- [ ] Lock features behind tier checks
- [ ] Show "Upgrade Required" modals for locked features
- [ ] Display tier-specific feature availability
- [ ] Implement soft limits with upgrade prompts

### Notification & Communication Tasks

#### 9. Email Notifications
- [ ] Trial started confirmation email
- [ ] 24-hour trial expiration warning email
- [ ] Trial expired + upgrade CTA email
- [ ] Weekly scan digest (Saver+ only)
- [ ] Invoice limit warning emails (80%, 95%, 100% of monthly limit)
- [ ] Subscription renewal reminders
- [ ] Failed payment notifications

#### 10. In-App Messaging
- [ ] Create notification center component
- [ ] Add tier-specific upgrade prompts
- [ ] Implement ROI calculator in upgrade flows
- [ ] Build "Money-back guarantee" messaging for Saver tier

---

## MEDIUM PRIORITY - Product Enhancements

### User Actions & Interactivity
- [ ] Implement "Mark as Resolved" backend logic
- [ ] Add "Dismiss" finding action
- [ ] Add notes/comments to findings
- [ ] Build vendor exclusion list management
- [ ] Create custom alert threshold settings

### Advanced Features
- [ ] Slack integration for notifications (Business tier)
- [ ] Team dashboard with read-only user roles (Business tier)
- [ ] API key generation and management (Business tier)
- [ ] Webhook configuration UI (Enterprise tier)
- [ ] Custom detection rules builder (Enterprise tier)

### Analytics & Reporting
- [ ] Build ROI tracking dashboard
- [ ] Create monthly executive summary report (Business tier)
- [ ] Add spending trend visualizations
- [ ] Implement vendor spending breakdown charts

---

## LOW PRIORITY - Polish & Optimization

### Performance
- [ ] Implement invoice processing queue for limits
- [ ] Add caching for frequently accessed data
- [ ] Optimize duplicate detection for large datasets
- [ ] Implement rate limiting per tier

### Testing
- [ ] Write tests for subscription tier enforcement
- [ ] Test Stripe webhook handling
- [ ] E2E test for upgrade flow
- [ ] Test trial expiration automation

### Documentation
- [ ] Create pricing page copy
- [ ] Write subscription management docs
- [ ] Document API access for Business tier
- [ ] Create enterprise onboarding guide

---

## Known Issues & Tech Debt

### Bugs to Fix
- [ ] Fix scan progress bar not updating properly
- [ ] Resolve console log showing scan job but no progress updates
- [ ] Fix duplicate invoice processing from same email with multiple PDFs
- [ ] Handle invoices with missing dates more gracefully

### Tech Debt
- [ ] Refactor scan processor to handle large email volumes
- [ ] Improve error handling in invoice parser
- [ ] Add retry logic for failed PDF downloads
- [ ] Implement proper logging and monitoring

---

## Definition of Done - Pricing Launch Checklist

### Backend
- [ ] All tier limits enforced in API
- [ ] Stripe integration complete and tested
- [ ] Trial expiration automation working
- [ ] Subscription webhooks handling all events
- [ ] Usage tracking accurate

### Frontend
- [ ] Pricing page live
- [ ] Checkout flow tested end-to-end
- [ ] Trial countdown timer working
- [ ] Upgrade CTAs placed strategically
- [ ] Subscription management UI complete

### Business
- [ ] Stripe account verified
- [ ] Payment processing tested in production
- [ ] Money-back guarantee policy defined
- [ ] Customer support process documented
- [ ] Terms of service updated with pricing

### Legal & Compliance
- [ ] Privacy policy updated
- [ ] Terms of service include subscription terms
- [ ] Refund policy documented
- [ ] PCI compliance verified (via Stripe)

---

## Estimated Timeline

**Phase 1: Core Pricing Backend (Week 1-2)**
- Database schema updates
- Tier enforcement logic
- Basic Stripe integration

**Phase 2: Frontend Pricing UI (Week 2-3)**
- Pricing page
- Checkout flow
- Trial countdown
- Upgrade prompts

**Phase 3: Notifications & Polish (Week 3-4)**
- Email notifications
- In-app messaging
- Testing and bug fixes

**Target Launch:** 4 weeks from start

---

## Success Metrics

### Conversion Targets
- Free → Saver conversion: 15%+
- Saver → Business upgrade: 5%+
- Average revenue per user (ARPU): $150+
- Churn rate: <5% monthly

### Product Metrics
- Average waste found per user: $3,200+
- Average invoices processed per Saver user: <800/month
- Trial completion rate: 80%+
- Upgrade within 48 hours of trial end: 25%+
