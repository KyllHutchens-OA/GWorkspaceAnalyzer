"""Test GPT-4o Mini invoice extraction"""
from app.services.invoice_parser import InvoiceParser
from pathlib import Path

parser = InvoiceParser(use_gpt=True)
pdf_path = Path('scripts/test_invoices/01_exact_duplicate_aws_first.pdf')

print('Testing GPT-4o Mini extraction...\n')

with open(pdf_path, 'rb') as f:
    result = parser.parse_pdf(f.read(), 'test.pdf')

if result.success:
    inv = result.invoice
    print('SUCCESS!')
    print(f'Vendor: {inv.vendor_name}')
    print(f'Invoice: {inv.invoice_number}')
    print(f'Amount: ${inv.amount}')
    print(f'Date: {inv.invoice_date}')
    print(f'Method: {inv.extraction_method}')
    print(f'Confidence: {inv.confidence_score:.2f}')
else:
    print(f'FAILED: {result.error}')
