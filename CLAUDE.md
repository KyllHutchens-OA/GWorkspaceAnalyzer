# GWorkspace Analyzer - Product Specification
do not use any emojis in code
## Overview
A Google Workspace add-on that automatically scans Gmail for invoices and receipts to identify duplicate charges, unnecessary subscriptions, and price increases, helping users save money on their business expenses.

## Core Value Proposition
**"You're wasting $X,XXX this month"** - Automated financial waste detection for businesses using Google Workspace.

## Product Features

### 1. Installation & Authorization
- **One-click install** from Google Workspace Marketplace
- **OAuth integration** with Gmail (restricted scope: invoices/receipts only)
- Privacy-focused: only accesses billing-related emails

### 2. Initial Scan (Free)
- Automatically scans **last 90 days** of Gmail inbox
- Identifies emails containing invoices, receipts, and billing statements
- Smart detection of invoice-related emails (PDFs, images, structured data)

### 3. Data Extraction
Extract key information from various formats:
- **Vendor/merchant name**
- **Amount charged**
- **Date of charge**
- **Invoice/receipt number**
- **Payment method** (optional)

**Supported formats:**
- PDF attachments
- Images (OCR required)
- HTML email receipts
- Structured data (JSON-LD, microdata)

### 4. Analysis Engine

#### A. Duplicate Detection
- **Exact duplicates**: Same invoice number charged multiple times
- **Probable duplicates**: Same vendor + same amount + different dates within 7 days
- **Confidence scoring**: High/Medium/Low likelihood of being a duplicate

#### B. Subscription Sprawl Detection
- Multiple accounts with same vendor (e.g., 3 different Zoom accounts)
- Unused seat detection (e.g., paying for 50 licenses, only 30 active)
- Overlapping services (e.g., Dropbox + Google Drive + OneDrive)
- Forgotten/abandoned subscriptions (no usage activity)

#### C. Price Creep Monitoring
- Month-over-month price comparisons by vendor
- Alert on increases >20% (configurable threshold)
- Annual price increase tracking
- Hidden fee detection

#### D. Anomaly Detection
- Unusual charge amounts
- Unexpected billing frequency changes
- New vendors not seen before

### 5. Dashboard & Reporting

#### Main Dashboard Features:
- **Headline metric**: "You're wasting $X,XXX this month"
- **Breakdown by category**:
  - Duplicate charges: $X,XXX
  - Unused subscriptions: $X,XXX
  - Price increases: $X,XXX
- **Action items list** (prioritized by savings potential)
- **Vendor list view** with spending trends
- **Timeline view** of all charges

#### Individual Issue Cards:
```
[!] Duplicate Charge - $2,499
Vendor: AWS
Invoice #12345 charged on Jan 15 and Jan 16
Confidence: 98% duplicate
[View Details] [Mark as Resolved] [Not a Duplicate]
```

### 6. Ongoing Monitoring
- **Weekly email digest**: "Found 3 new issues worth $2,300"
- Real-time alerts for high-value duplicates (>$1,000)
- Monthly summary report
- Trend analysis (spending up/down vs previous period)

### 7. User Actions
Users can:
- Mark issues as "Resolved" or "Not an Issue"
- Add notes to charges
- Exclude specific vendors from analysis
- Export reports (PDF/CSV)
- Set custom alert thresholds
- Configure notification preferences

## Technical Requirements

### Frontend (Next.js)
- Dashboard with data visualizations (charts, tables)
- Invoice viewer/preview
- Settings & preferences page
- Notification center
- Mobile-responsive design

### Backend (FastAPI)
- Gmail API integration
- Invoice parsing service (PDF + OCR)
- Duplicate detection algorithm
- Subscription tracking logic
- Price change detection
- Email notification service
- Data storage (invoice metadata, analysis results)

### Google Workspace Integration
- Google Workspace Marketplace listing
- OAuth 2.0 with Gmail API scopes:
  - `gmail.readonly` (or more restricted scope if available)
- Webhook/Push notifications for new emails (optional)

### Data Processing Pipeline
1. **Email fetching**: Gmail API queries for billing-related emails
2. **Classification**: ML model to identify invoice/receipt emails
3. **Extraction**: Parse PDFs, OCR images, extract structured data
4. **Normalization**: Standardize vendor names, amounts, dates
5. **Analysis**: Run duplicate detection, subscription tracking, price monitoring
6. **Storage**: Save results to database
7. **Notification**: Generate alerts and weekly digests

### Required Integrations
- **Gmail API**: Email access
- **Google OAuth**: Authentication
- **PDF parsing**: PyPDF2, pdfplumber, or similar
- **OCR**: Google Cloud Vision API or Tesseract
- **Email sending**: SendGrid, AWS SES, or Google SMTP

## Business Model

### Pricing Tiers
1. **Free Tier (Trial)**
   - One-time initial 90-day scan
   - Full analysis report
   - Dashboard access for 7 days
   - No ongoing monitoring

2. **Pro Tier - $49/month**
   - Continuous monitoring
   - Weekly email digests
   - Real-time alerts
   - Unlimited historical scans
   - Priority support
   - Export reports

3. **Enterprise Tier** (Future)
   - Team/organization-wide deployment
   - Multi-account management
   - Custom integrations
   - Dedicated support

### Conversion Strategy
1. Free scan shows immediate value ("You're wasting $X,XXX")
2. 7-day dashboard access creates urgency
3. Weekly digest emails keep users engaged
4. Clear ROI: Saving $2,300/month for $49/month = 47x return

## User Journey Flow

```
1. User installs add-on from Google Workspace Marketplace
   ↓
2. OAuth authorization (Gmail read access)
   ↓
3. "Scanning your inbox..." (processing message)
   ↓
4. Initial scan complete: "Found 127 invoices, analyzed for issues"
   ↓
5. Dashboard reveals: "You're wasting $4,850 this month"
   ↓
6. User explores issues (duplicates, unused subscriptions, price increases)
   ↓
7. User marks some issues as resolved
   ↓
8. Day 5: Email reminder "Your free trial ends in 2 days"
   ↓
9. Day 7: Trial expires, CTA to subscribe ($49/month)
   ↓
10. Subscribe → Continuous monitoring begins
    ↓
11. Weekly email: "Found 2 new issues worth $1,200"
```

## Key Metrics to Track

### Product Metrics
- Number of scans completed
- Average invoices found per user
- Average "waste" detected per user
- Issue types breakdown (duplicates vs subscriptions vs price increases)
- User actions taken (resolved, dismissed, etc.)

### Business Metrics
- Free trial → Paid conversion rate
- Monthly recurring revenue (MRR)
- Customer lifetime value (LTV)
- Churn rate
- Net Promoter Score (NPS)

### Technical Metrics
- Email parsing accuracy
- Duplicate detection precision/recall
- API rate limit usage
- Processing time per scan
- Error rates

## Privacy & Security Considerations

- **Minimal data access**: Only invoice/receipt emails (not personal emails)
- **Data encryption**: At rest and in transit
- **Data retention**: User controls, option to delete all data
- **No third-party sharing**: User data never sold or shared
- **Compliance**: GDPR, CCPA, SOC 2 (as needed)
- **Transparent permissions**: Clear explanation of why each permission is needed

## Development Phases

### Phase 1: MVP (Months 1-3)
- [ ] Gmail OAuth integration
- [ ] Basic invoice detection (PDF parsing only)
- [ ] Duplicate detection (exact matches)
- [ ] Simple dashboard
- [ ] Initial 90-day scan
- [ ] Google Workspace Marketplace listing

### Phase 2: Analysis Enhancement (Months 3-4)
- [ ] OCR for image invoices
- [ ] Probable duplicate detection
- [ ] Subscription tracking
- [ ] Price monitoring
- [ ] Weekly email digests

### Phase 3: User Experience (Months 4-5)
- [ ] Improved dashboard with visualizations
- [ ] User actions (resolve, dismiss, notes)
- [ ] Export reports
- [ ] Mobile responsiveness
- [ ] Onboarding flow optimization

### Phase 4: Growth & Scale (Months 5-6)
- [ ] Payment processing (Stripe)
- [ ] Email marketing automation
- [ ] Analytics dashboard
- [ ] Performance optimization
- [ ] Customer support system

### Phase 5: Advanced Features (Future)
- [ ] Bank account integration (Plaid)
- [ ] Calendar integration (meeting cost analysis)
- [ ] Vendor negotiation suggestions
- [ ] Team/enterprise features
- [ ] API for third-party integrations

## Success Criteria

### Technical Success
- 95%+ uptime
- <30 seconds average scan time
- 90%+ invoice detection accuracy
- 85%+ duplicate detection precision

### Business Success
- 1,000 free trial users in first 3 months
- 15%+ free → paid conversion rate
- $10,000+ MRR by month 6
- <5% monthly churn rate

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Low invoice detection accuracy | High | Train ML model, iterate on parsing logic, manual review option |
| False positive duplicates | Medium | Confidence scoring, user feedback loop |
| Gmail API rate limits | High | Implement queuing, batch processing, optimize queries |
| Privacy concerns | High | Transparent communication, minimal data access, user controls |
| Low conversion rate | High | A/B testing, improve value demonstration, reduce friction |
| Google Workspace approval delay | Medium | Start approval process early, follow guidelines exactly |

## Competitive Landscape

### Existing Solutions
- **Expensify, Concur**: Expense management (manual upload)
- **Divvy, Ramp**: Corporate cards (requires switching payment method)
- **Duplicate payment tools**: Often accounting software plugins

### Competitive Advantages
- **Zero effort**: Fully automatic, no manual uploads
- **Works with existing tools**: No need to change payment methods
- **Gmail-native**: Lives where invoices already are
- **Free initial value**: Try before you buy

## Next Steps for Development

1. **Set up Google Cloud Project** for Gmail API access
2. **Build OAuth flow** with appropriate scopes
3. **Implement Gmail query** to find invoice-related emails
4. **Develop PDF parser** for invoice data extraction
5. **Create duplicate detection algorithm**
6. **Build dashboard UI** with Next.js + Tailwind
7. **Implement backend API** with FastAPI
8. **Test with real Gmail accounts** (beta users)
9. **Submit to Google Workspace Marketplace**
10. **Launch marketing campaign**

---

## Notes for AI Assistant (Claude)

When working on this project:
- Prioritize **invoice detection accuracy** - this is the foundation
- Keep **user privacy** top of mind in all decisions
- Focus on **quick value delivery** (initial scan must wow users)
- **Iterate based on data** - track which issues users care about most
- **Security first** - handle OAuth tokens and user data carefully
- Consider **rate limits** early (Gmail API has quotas)
- Design for **scale** from the start (database indexes, caching, async processing)
