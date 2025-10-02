# GPT-4o Mini Invoice Extraction Setup

The system now uses OpenAI's GPT-4o Mini for intelligent invoice data extraction, replacing regex-based parsing for much better accuracy.

## Why GPT-4o Mini?

- **Better extraction**: Handles any invoice format automatically
- **No regex maintenance**: No need to update patterns for each vendor
- **Higher accuracy**: Correctly identifies vendor names, amounts, dates, invoice numbers
- **Cost-effective**: GPT-4o Mini is very affordable (~$0.15 per 1M input tokens)

## Setup Instructions

### 1. Get an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### 2. Add to Environment Variables

Add to `backend/.env`:

```bash
# OpenAI API (for GPT-4o Mini invoice extraction)
OPENAI_API_KEY="sk-your-actual-api-key-here"

# Feature Flags
USE_GPT_EXTRACTION=true  # Enable GPT extraction (recommended)
```

### 3. Install Dependencies

```bash
cd backend
pip install openai==1.12.0
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

### 4. Test the Integration

Test GPT extraction on a sample PDF:

```bash
cd backend
python -c "
from app.services.invoice_parser import InvoiceParser
from pathlib import Path

parser = InvoiceParser(use_gpt=True)
pdf_path = Path('scripts/test_invoices/01_exact_duplicate_aws_first.pdf')

with open(pdf_path, 'rb') as f:
    result = parser.parse_pdf(f.read(), 'test.pdf')

if result.success:
    inv = result.invoice
    print(f'SUCCESS!')
    print(f'Vendor: {inv.vendor_name}')
    print(f'Invoice #: {inv.invoice_number}')
    print(f'Amount: \${inv.amount}')
    print(f'Date: {inv.invoice_date}')
    print(f'Extraction method: {inv.extraction_method}')
else:
    print(f'FAILED: {result.error}')
"
```

Expected output:
```
SUCCESS!
Vendor: Amazon Web Services
Invoice #: AWS-12345
Amount: $2499.00
Date: 2024-01-16
Extraction method: gpt4o_mini
```

## How It Works

### Pipeline Flow

1. **Email Scan**: Gmail API finds potential invoice emails
2. **Text Extraction**: PDF text is extracted using pdfplumber/PyPDF2
3. **GPT Analysis**: Text is sent to GPT-4o Mini with structured prompt
4. **Data Extraction**: GPT returns JSON with vendor, amount, date, invoice #
5. **Validation**: Data is validated and stored in database
6. **Duplicate Detection**: Invoices are analyzed for duplicates, price increases, etc.

### GPT Prompt Structure

The system sends this to GPT-4o Mini:

```
Extract the following information from this invoice:
- vendor_name: Company that issued the invoice
- invoice_number: Invoice or order number
- invoice_date: Date in YYYY-MM-DD format
- total_amount: Total amount as number
- currency: Currency code (USD, EUR, etc.)
- is_invoice: true/false

Return JSON only.
```

### Fallback Mode

If GPT extraction fails or is disabled, the system falls back to regex-based extraction automatically.

## Cost Estimation

GPT-4o Mini pricing (as of 2025):
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens

**Example calculation:**
- Average invoice: ~1,000 tokens input, ~100 tokens output
- Cost per invoice: ~$0.00015 input + $0.00006 output = **$0.0002 per invoice**
- 1,000 invoices: ~$0.20
- 10,000 invoices: ~$2.00

**Extremely affordable** for the accuracy improvement!

## Configuration Options

### Enable/Disable GPT Extraction

In `backend/.env`:
```bash
USE_GPT_EXTRACTION=true   # Use GPT (recommended)
USE_GPT_EXTRACTION=false  # Use regex fallback
```

### Programmatic Control

```python
from app.services.invoice_parser import InvoiceParser

# Force GPT mode
parser = InvoiceParser(use_gpt=True)

# Force regex mode
parser = InvoiceParser(use_gpt=False)
```

## Monitoring & Debugging

### Check Logs

The system logs extraction method used:

```
INFO: Using GPT-4o Mini for invoice extraction
INFO: GPT extracted: Amazon Web Services - $2499.00
```

### Check Database

Invoices store the extraction method:

```sql
SELECT vendor_name, amount, extraction_method
FROM invoices
ORDER BY created_at DESC
LIMIT 10;
```

Values:
- `gpt4o_mini` - Extracted with GPT
- `pdf_regex` - Extracted with regex fallback
- `gpt_failed` - GPT failed, minimal data stored

## Troubleshooting

### Error: "OPENAI_API_KEY not set"

**Solution**: Add your OpenAI API key to `backend/.env`

### Error: "OpenAI API key invalid"

**Solution**:
1. Check your API key at https://platform.openai.com/api-keys
2. Ensure it starts with `sk-`
3. Make sure there are no extra spaces in `.env`

### Error: "Rate limit exceeded"

**Solution**:
1. Check your OpenAI usage at https://platform.openai.com/usage
2. Upgrade your OpenAI plan if needed
3. Add delays between requests in `scan_processor.py`

### GPT returns wrong data

**Check**:
1. The PDF text extraction quality (log `text[:500]`)
2. The GPT response JSON (add debug logging)
3. Try adjusting the temperature (currently 0 for deterministic output)

## Next Steps

1. Add your OpenAI API key to `backend/.env`
2. Restart your backend server
3. Run a new scan to test GPT extraction
4. Monitor costs at https://platform.openai.com/usage
5. Adjust `USE_GPT_EXTRACTION` flag if needed

## Support

If you encounter issues:
1. Check logs: `backend/logs/app.log`
2. Test individual PDFs using the test script above
3. Verify your OpenAI API key is valid
4. Check OpenAI status: https://status.openai.com/
