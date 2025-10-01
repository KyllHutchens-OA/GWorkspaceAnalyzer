# Gmail Service Documentation

## Overview

The `GmailService` class handles all Gmail API interactions for scanning and retrieving invoice-related emails.

## Features

### 1. Email Search
- **`search_invoice_emails(start_date, end_date, max_results)`**
  - Searches for emails containing invoices/receipts
  - Uses intelligent query building with keywords and file types
  - Default: scans last 90 days
  - Returns list of message IDs

### 2. Email Retrieval
- **`get_email_details(message_id)`**
  - Fetches full email including headers, body, and attachments
  - Extracts metadata (subject, sender, date)
  - Decodes base64-encoded content

- **`batch_get_emails(message_ids)`**
  - Efficiently fetches multiple emails
  - Handles batching (100 emails per batch)
  - Error-resistant (continues on individual failures)

### 3. Attachment Handling
- **`download_attachment(message_id, attachment_id)`**
  - Downloads email attachments as bytes
  - Handles base64 decoding
  - Supports PDFs, images, etc.

### 4. Invoice Detection
- **`is_invoice_related(email)`**
  - AI-powered detection of invoice/receipt emails
  - Checks subject, body, and attachments
  - Returns boolean confidence

### 5. User Profile
- **`get_user_profile()`**
  - Returns authenticated user's Gmail profile
  - Email address, message count, thread count

## Usage Example

```python
from app.services import GmailService
from datetime import datetime, timedelta

# Initialize with user's OAuth credentials
user_creds = {
    "token": "ya29.a0...",  # From Supabase
    "refresh_token": "1//...",
    "client_id": settings.GOOGLE_CLIENT_ID,
    "client_secret": settings.GOOGLE_CLIENT_SECRET,
}

gmail = GmailService(user_creds)

# Search for invoices in last 90 days
messages = gmail.search_invoice_emails(
    start_date=datetime.now() - timedelta(days=90),
    max_results=500
)

# Get details for each message
for msg in messages[:10]:  # First 10
    email = gmail.get_email_details(msg['id'])

    if gmail.is_invoice_related(email):
        print(f"Invoice: {email['subject']}")

        # Download attachments
        for att in email['attachments']:
            data = gmail.download_attachment(msg['id'], att['attachment_id'])
            # Save or process attachment
```

## Search Query Logic

The service builds intelligent Gmail queries:

```
(invoice OR receipt OR payment OR billing OR order confirmation OR purchase OR subscription OR charge OR paid)
OR (filename:pdf OR filename:jpg OR filename:png OR filename:jpeg)
after:2024/01/01 before:2024/04/01
has:attachment OR subject:(invoice OR receipt OR billing)
```

## Keywords Detected

### Invoice Indicators:
- invoice
- receipt
- payment
- billing
- order confirmation
- purchase
- subscription
- charge
- paid
- amount due
- total

### File Types:
- PDF (most common)
- JPG/JPEG
- PNG

## Error Handling

All methods handle `HttpError` from Gmail API:
- Log errors
- Re-raise for handling at higher level
- Batch operations continue on individual failures

## Authentication

Requires OAuth 2.0 credentials with scopes:
- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/userinfo.email`
- `https://www.googleapis.com/auth/userinfo.profile`

## Rate Limits

Gmail API quotas (per user per day):
- **Quota units**: 1 billion/day
- **Read requests**: 5 units each
- **Typical usage**: ~50,000 email reads/day

## Next Steps

1. **OAuth Flow**: Implement authentication endpoints
2. **Token Storage**: Store refresh tokens in Supabase Vault
3. **Scan Jobs**: Create background job to process emails
4. **Invoice Parsing**: Extract data from email/attachments
5. **Database Storage**: Save invoices to Supabase
