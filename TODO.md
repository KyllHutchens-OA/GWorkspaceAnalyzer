# Spend Analyzer for Google Workspace - Development Tasks

## Phase 1: Core Infrastructure (MVP)

### Database (1 task)
- [ ] Design and implement database schema for invoices, vendors, charges, and user data

### Google OAuth & Gmail Integration (3 tasks)
- [ ] Set up Google Cloud Project and enable Gmail API
- [ ] Implement Google OAuth 2.0 flow for Gmail authentication
- [ ] Build Gmail API integration to fetch invoice/receipt emails

### Invoice Extraction (3 tasks)
- [ ] Implement PDF text extraction for invoices
- [ ] Build invoice data parser (vendor, amount, date, invoice number)
- [ ] Create vendor name normalization logic

### Analysis Algorithms (5 tasks)
- [ ] Implement exact duplicate detection algorithm
- [ ] Implement probable duplicate detection algorithm
- [ ] Build subscription tracking logic (same vendor, recurring charges)
- [ ] Implement price monitoring system (month-over-month increases)
- [ ] Create analysis engine to calculate total waste amount

### Frontend Dashboard (5 tasks)
- [ ] Build frontend authentication pages (login, OAuth callback)
- [ ] Create dashboard homepage with headline waste metric
- [ ] Build issue cards component (duplicate charges, subscriptions, price increases)
- [ ] Create vendor list view with spending trends
- [ ] Implement invoice detail viewer/preview

### User Actions & Settings (2 tasks)
- [ ] Build user action endpoints (mark resolved, dismiss, add notes)
- [ ] Create settings page (alert thresholds, excluded vendors, notifications)

## Phase 2: Engagement & Monetization

### Email Notifications (2 tasks)
- [ ] Implement weekly email digest system
- [ ] Set up email service integration (SendGrid or AWS SES)

### Infrastructure & Performance (2 tasks)
- [ ] Build async job queue for email processing
- [ ] Implement rate limiting for Gmail API calls

### User Experience (1 task)
- [ ] Create onboarding flow (initial scan, loading screen, results reveal)

### Payment & Subscriptions (3 tasks)
- [ ] Set up Stripe integration for payment processing
- [ ] Build subscription management endpoints (upgrade, cancel)
- [ ] Implement free trial logic (7-day access, then paywall)

## Phase 3: Distribution & Advanced Features

### Marketplace (1 task)
- [ ] Create Google Workspace Marketplace listing

### OCR Support - Phase 2 (2 tasks)
- [ ] Set up Google Cloud Vision API for OCR
- [ ] Implement image invoice processing with OCR

---

## Progress Summary
- Total Tasks: 30
- Completed: 0
- In Progress: 0
- Pending: 30

## Priority Order for MVP Launch
1. Database schema
2. Google OAuth and Gmail integration
3. PDF invoice extraction
4. Duplicate detection (exact matches)
5. Basic frontend dashboard
6. Email notification system
7. Google Workspace Marketplace listing

## Notes
- Start with PDF-only support (no OCR) for MVP
- Focus on exact duplicate detection first
- Weekly email digests are critical for user retention
- Free trial → paid conversion is the key metric
