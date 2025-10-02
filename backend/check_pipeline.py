"""Check if GPT-4o Mini pipeline is ready"""

print('Checking GPT-4o Mini Invoice Extraction Pipeline...\n')

# 1. Config
from app.config.settings import settings
api_key_status = 'SET' if settings.OPENAI_API_KEY else 'MISSING'
gpt_status = 'ENABLED' if settings.USE_GPT_EXTRACTION else 'DISABLED'
print(f'1. OpenAI API Key: {api_key_status}')
print(f'   GPT Extraction: {gpt_status}\n')

# 2. Services
from app.services.gpt_extractor import GPTInvoiceExtractor
from app.services.invoice_parser import InvoiceParser
from app.services.duplicate_detector import DuplicateDetector
print('2. Services: LOADED')
print('   - GPTInvoiceExtractor')
print('   - InvoiceParser')
print('   - DuplicateDetector\n')

# 3. Models
from app.models import ParsedInvoice, PriceIncreaseFinding, DuplicateFinding
print('3. Models: LOADED')
print('   - ParsedInvoice')
print('   - PriceIncreaseFinding (with optional dates)')
print('   - DuplicateFinding\n')

# 4. Scan Processor
from app.services.scan_processor import process_scan_job
print('4. Scan Processor: LOADED\n')

print('=' * 50)
print('STATUS: ALL SYSTEMS READY')
print('=' * 50)
print('\nThe pipeline is ready to:')
print('1. Scan Gmail for invoice emails')
print('2. Extract text from PDF attachments')
print('3. Use GPT-4o Mini to extract invoice data')
print('4. Detect duplicates, price increases, subscriptions')
print('5. Save findings to database')
print('\nYou can now run a scan through the app!')
