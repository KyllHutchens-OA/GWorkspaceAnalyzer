# Test Invoice Generator

This script generates realistic invoice PDFs for testing the duplicate detection and analysis system.

## Quick Start

```bash
# Install dependencies
pip install reportlab

# Generate test invoices
cd backend/scripts
python generate_test_invoices.py
```

This will create a `test_invoices/` directory with ~50 PDF files.

## Test Scenarios

### 1. Exact Duplicates (98% confidence)
**Should be flagged as definite duplicates**

- **AWS Duplicate**: Same invoice #AWS-12345 charged twice ($2,499 on Jan 15 & 16)
- **Stripe Triple**: Invoice #INV-001-STRIPE appears 3 times in 3 days ($299 each)

**Expected behavior**: System flags with high confidence, counts as waste

### 2. Probable Duplicates (50% confidence)
**Should be flagged for user review**

- **DigitalOcean**: $99.99 charged 1 day apart (different invoice numbers)
- **GitHub**: $49.00 charged 2 days apart (different invoice numbers)

**Expected behavior**: Flagged for review, NOT counted as guaranteed waste, shows "potential_waste" in details

### 3. Price Increases (90% confidence)
**Should detect significant price jumps**

- **Zoom**: $149 → $199 (33% increase, month-over-month)
- **Salesforce**: $5,000 → $6,500 (30% increase, quarter-over-quarter)

**Expected behavior**: Flagged when increase ≥20%

### 4. Subscription Sprawl
**Multiple accounts with same vendor**

- **Dropbox**: 3 separate accounts ($15, $20, $15/month) each billed 3 times
- **Slack**: 3 workspaces (Engineering, Marketing, Sales) at $80/month each

**Expected behavior**: Should identify multiple recurring subscriptions to same vendor

### 5. Regular Subscriptions (Should NOT Flag)
**Normal recurring charges that should be ignored**

- **Netflix**: Consistent $15.99 every 30 days (6 months)
- **AWS Monthly**: Varying amounts monthly (normal usage fluctuation)
- **Adobe Annual**: $599.88 charged exactly 365 days apart

**Expected behavior**: Detected as legitimate subscriptions, NOT flagged as duplicates

### 6. Edge Cases (Boundary Testing)

- **Asana**: 19% increase (below 20% threshold) - should NOT flag
- **Monday.com**: 21% increase (above 20% threshold) - should flag
- **Heroku**: $75 charged exactly 7 days apart - tests duplicate detection window

## File Naming Convention

Files are named to clearly indicate their purpose:
```
01_exact_duplicate_aws_first.pdf
02_probable_duplicate_do_first.pdf
03_price_increase_zoom_before.pdf
04_subscription_sprawl_dropbox_acct1_month1.pdf
05_regular_subscription_netflix_month1.pdf
06_edge_case_asana_19pct_before.pdf
```

Prefix numbers:
- `01_` = Exact duplicates
- `02_` = Probable duplicates
- `03_` = Price increases
- `04_` = Subscription sprawl
- `05_` = Regular subscriptions
- `06_` = Edge cases

## Expected Detection Results

When you scan these invoices, you should see:

### Duplicates Tab
- 2 exact duplicate findings (AWS + Stripe)
- 2 probable duplicate findings requiring review (DigitalOcean + GitHub)

### Price Increases Tab
- 2 price increase findings (Zoom + Salesforce)
- Monday.com (21% increase)

### Subscription Sprawl Tab
- 3 Dropbox accounts
- 3 Slack workspaces

### Should NOT Appear
- Netflix monthly charges (regular 30-day pattern)
- AWS varying monthly bills (normal usage)
- Adobe annual renewal (365 days apart)
- Asana 19% increase (below threshold)
- Heroku charges 7 days apart (outside 2-day duplicate window)

## Testing Workflow

### Option A: Manual Gmail Upload
1. Create a test Gmail account
2. Send emails with these PDFs as attachments
3. Use invoice-related keywords in subject lines
4. Run your app's scan feature

### Option B: Automated Email Sending
```python
# Add this to generate_test_invoices.py for automated sending
# Requires Gmail API setup

from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_test_emails(gmail_service, pdf_files):
    for pdf_path in pdf_files:
        message = MIMEMultipart()
        message['subject'] = f'Invoice: {os.path.basename(pdf_path)}'

        with open(pdf_path, 'rb') as f:
            pdf = MIMEApplication(f.read(), _subtype='pdf')
            pdf.add_header('Content-Disposition', 'attachment',
                          filename=os.path.basename(pdf_path))
            message.attach(pdf)

        # Send via Gmail API
        gmail_service.send_email(message)
```

### Option C: Direct Database Insert
For faster testing, you could also:
1. Parse the PDFs directly with your invoice parser
2. Insert results directly into your test database
3. Run analysis without Gmail API

## Customization

Edit `generate_test_invoices.py` to:

- Change amounts: Modify `Decimal()` values
- Adjust dates: Change `base_date + timedelta(days=X)`
- Add vendors: Call `generate_invoice()` with new companies
- Modify line items: Pass custom `line_items` list
- Change thresholds: Test different duplicate windows or price increase percentages

## Validation

After scanning, verify:

1. **Total invoices found**: ~50 PDFs
2. **Exact duplicates**: 2 findings (AWS + Stripe)
3. **Probable duplicates**: 2 findings for review
4. **Price increases**: 3 findings (Zoom, Salesforce, Monday.com)
5. **Subscription sprawl**: 6 accounts (3 Dropbox + 3 Slack)
6. **False positives**: 0 (no Netflix, AWS monthly, or Adobe flagged)

## Troubleshooting

**Issue**: PDFs not being detected as invoices
- Check Gmail search query includes keywords like "invoice", "billing"
- Verify email subjects contain invoice-related terms
- Ensure PDFs have .pdf extension

**Issue**: Duplicates not being detected
- Check `duplicate_window_days` parameter (default: 2 days for probable)
- Verify invoice numbers are being extracted correctly
- Review vendor name normalization

**Issue**: Regular subscriptions being flagged
- Check `_is_likely_subscription()` logic
- Verify subscription pattern detection (weekly/monthly/annual)
- Adjust tolerance values if needed

## Next Steps

1. **Run the generator**: `python generate_test_invoices.py`
2. **Upload to test Gmail**: Send PDFs as email attachments
3. **Scan with your app**: Trigger a 90-day scan
4. **Verify results**: Compare findings against expected results above
5. **Iterate on detection**: Adjust algorithms based on false positives/negatives
