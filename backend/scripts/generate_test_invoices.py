"""
Generate test invoice PDFs for testing the duplicate detection system

This script creates realistic invoice PDFs with controlled scenarios:
- Exact duplicates (same invoice number, amount)
- Probable duplicates (same vendor/amount, close dates)
- Price increases
- Subscription sprawl
- Regular subscriptions (should NOT be flagged)
"""
import os
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors


class InvoiceGenerator:
    """Generate realistic invoice PDFs"""

    def __init__(self, output_dir: str = "test_invoices"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_invoice(
        self,
        vendor_name: str,
        amount: Decimal,
        invoice_number: str,
        invoice_date: datetime,
        due_date: datetime = None,
        line_items: List[Dict[str, Any]] = None,
        filename: str = None,
    ) -> str:
        """
        Generate a single invoice PDF

        Args:
            vendor_name: Company name
            amount: Total amount
            invoice_number: Invoice number
            invoice_date: Invoice date
            due_date: Due date (default: 30 days after invoice)
            line_items: List of {description, quantity, unit_price}
            filename: Custom filename (default: auto-generated)

        Returns:
            Path to generated PDF
        """
        if not due_date:
            due_date = invoice_date + timedelta(days=30)

        if not filename:
            date_str = invoice_date.strftime("%Y%m%d")
            filename = f"{vendor_name.replace(' ', '_')}_{invoice_number}_{date_str}.pdf"

        filepath = os.path.join(self.output_dir, filename)

        # Create PDF
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter

        # Header - Vendor info
        c.setFont("Helvetica-Bold", 20)
        c.drawString(1 * inch, height - 1 * inch, vendor_name)

        c.setFont("Helvetica", 10)
        c.drawString(1 * inch, height - 1.3 * inch, "123 Business St")
        c.drawString(1 * inch, height - 1.5 * inch, "San Francisco, CA 94105")
        c.drawString(1 * inch, height - 1.7 * inch, f"support@{vendor_name.lower().replace(' ', '')}.com")

        # Invoice title
        c.setFont("Helvetica-Bold", 24)
        c.drawString(1 * inch, height - 2.5 * inch, "INVOICE")

        # Invoice details
        c.setFont("Helvetica", 11)
        c.drawString(1 * inch, height - 3 * inch, f"Invoice Number: {invoice_number}")
        c.drawString(1 * inch, height - 3.2 * inch, f"Invoice Date: {invoice_date.strftime('%B %d, %Y')}")
        c.drawString(1 * inch, height - 3.4 * inch, f"Due Date: {due_date.strftime('%B %d, %Y')}")

        # Bill To section
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, height - 4 * inch, "Bill To:")
        c.setFont("Helvetica", 10)
        c.drawString(1 * inch, height - 4.2 * inch, "Test Company Inc")
        c.drawString(1 * inch, height - 4.4 * inch, "456 Client Ave")
        c.drawString(1 * inch, height - 4.6 * inch, "New York, NY 10001")

        # Line items table
        y_position = height - 5.2 * inch

        # Table header
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1 * inch, y_position, "Description")
        c.drawString(4.5 * inch, y_position, "Quantity")
        c.drawString(5.5 * inch, y_position, "Unit Price")
        c.drawString(6.5 * inch, y_position, "Amount")

        # Draw line under header
        y_position -= 0.1 * inch
        c.line(1 * inch, y_position, 7.5 * inch, y_position)

        # Line items
        c.setFont("Helvetica", 10)
        y_position -= 0.2 * inch

        if not line_items:
            # Default line item
            line_items = [
                {
                    "description": f"{vendor_name} Monthly Subscription",
                    "quantity": 1,
                    "unit_price": float(amount),
                }
            ]

        for item in line_items:
            desc = item["description"]
            qty = item["quantity"]
            unit_price = item["unit_price"]
            line_total = qty * unit_price

            c.drawString(1 * inch, y_position, desc)
            c.drawRightString(5 * inch, y_position, str(qty))
            c.drawRightString(6.2 * inch, y_position, f"${unit_price:.2f}")
            c.drawRightString(7.3 * inch, y_position, f"${line_total:.2f}")

            y_position -= 0.2 * inch

        # Totals
        y_position -= 0.3 * inch
        c.line(5.5 * inch, y_position, 7.5 * inch, y_position)

        y_position -= 0.3 * inch
        c.setFont("Helvetica-Bold", 11)
        c.drawString(5.5 * inch, y_position, "Subtotal:")
        c.drawRightString(7.3 * inch, y_position, f"${float(amount):.2f}")

        y_position -= 0.2 * inch
        c.setFont("Helvetica", 10)
        c.drawString(5.5 * inch, y_position, "Tax:")
        c.drawRightString(7.3 * inch, y_position, "$0.00")

        y_position -= 0.3 * inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(5.5 * inch, y_position, "TOTAL:")
        c.drawRightString(7.3 * inch, y_position, f"${float(amount):.2f}")

        # Payment terms
        y_position -= 0.8 * inch
        c.setFont("Helvetica", 9)
        c.drawString(1 * inch, y_position, "Payment Terms: Net 30 days")
        y_position -= 0.2 * inch
        c.drawString(1 * inch, y_position, "Make checks payable to: " + vendor_name)

        # Footer
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(
            width / 2,
            0.5 * inch,
            f"Thank you for your business! | {vendor_name} | Invoice #{invoice_number}"
        )

        c.save()

        print(f"Generated: {filepath}")
        return filepath


def generate_test_scenarios():
    """Generate all test scenarios"""
    generator = InvoiceGenerator()
    base_date = datetime(2024, 1, 1)

    print("\n=== Generating Test Invoice PDFs ===\n")

    # ===== EXACT DUPLICATES =====
    print("1. EXACT DUPLICATES (should flag with 98% confidence)")

    # Scenario 1A: AWS charged twice with same invoice number
    generator.generate_invoice(
        vendor_name="Amazon Web Services",
        amount=Decimal("2499.00"),
        invoice_number="AWS-12345",
        invoice_date=base_date + timedelta(days=15),
        filename="01_exact_duplicate_aws_first.pdf"
    )
    generator.generate_invoice(
        vendor_name="Amazon Web Services",
        amount=Decimal("2499.00"),
        invoice_number="AWS-12345",
        invoice_date=base_date + timedelta(days=16),
        filename="01_exact_duplicate_aws_second.pdf"
    )

    # Scenario 1B: Stripe invoice appearing 3 times
    for i in range(3):
        generator.generate_invoice(
            vendor_name="Stripe",
            amount=Decimal("299.00"),
            invoice_number="INV-001-STRIPE",
            invoice_date=base_date + timedelta(days=20 + i),
            filename=f"01_exact_duplicate_stripe_{i+1}.pdf"
        )

    # ===== PROBABLE DUPLICATES =====
    print("\n2. PROBABLE DUPLICATES (should flag for review)")

    # Scenario 2A: Same vendor, same amount, 1 day apart (no invoice number match)
    generator.generate_invoice(
        vendor_name="DigitalOcean",
        amount=Decimal("99.99"),
        invoice_number="DO-5001",
        invoice_date=base_date + timedelta(days=30),
        filename="02_probable_duplicate_do_first.pdf"
    )
    generator.generate_invoice(
        vendor_name="DigitalOcean",
        amount=Decimal("99.99"),
        invoice_number="DO-5002",
        invoice_date=base_date + timedelta(days=31),
        filename="02_probable_duplicate_do_second.pdf"
    )

    # Scenario 2B: GitHub charges 2 days apart
    generator.generate_invoice(
        vendor_name="GitHub",
        amount=Decimal("49.00"),
        invoice_number="GH-2024-001",
        invoice_date=base_date + timedelta(days=40),
        filename="02_probable_duplicate_github_first.pdf"
    )
    generator.generate_invoice(
        vendor_name="GitHub",
        amount=Decimal("49.00"),
        invoice_number="GH-2024-002",
        invoice_date=base_date + timedelta(days=42),
        filename="02_probable_duplicate_github_second.pdf"
    )

    # ===== PRICE INCREASES =====
    print("\n3. PRICE INCREASES (should flag increases >20%)")

    # Scenario 3A: Zoom price increase 33%
    generator.generate_invoice(
        vendor_name="Zoom",
        amount=Decimal("149.00"),
        invoice_number="ZOOM-JAN-2024",
        invoice_date=base_date + timedelta(days=0),
        filename="03_price_increase_zoom_before.pdf"
    )
    generator.generate_invoice(
        vendor_name="Zoom",
        amount=Decimal("199.00"),
        invoice_number="ZOOM-FEB-2024",
        invoice_date=base_date + timedelta(days=30),
        filename="03_price_increase_zoom_after.pdf"
    )

    # Scenario 3B: Salesforce price increase 30%
    generator.generate_invoice(
        vendor_name="Salesforce",
        amount=Decimal("5000.00"),
        invoice_number="SF-Q1-2024",
        invoice_date=base_date + timedelta(days=0),
        filename="03_price_increase_salesforce_before.pdf"
    )
    generator.generate_invoice(
        vendor_name="Salesforce",
        amount=Decimal("6500.00"),
        invoice_number="SF-Q2-2024",
        invoice_date=base_date + timedelta(days=90),
        filename="03_price_increase_salesforce_after.pdf"
    )

    # ===== SUBSCRIPTION SPRAWL =====
    print("\n4. SUBSCRIPTION SPRAWL (multiple accounts with same vendor)")

    # Scenario 4A: 3 different Dropbox accounts
    for i in range(3):
        amount = Decimal("15.00") if i != 1 else Decimal("20.00")  # Different tiers
        for month in range(3):  # 3 months of charges
            generator.generate_invoice(
                vendor_name="Dropbox",
                amount=amount,
                invoice_number=f"DBX-ACCT{i+1}-{month+1:02d}",
                invoice_date=base_date + timedelta(days=month * 30 + i),
                filename=f"04_subscription_sprawl_dropbox_acct{i+1}_month{month+1}.pdf"
            )

    # Scenario 4B: Multiple Slack workspaces
    workspaces = ["Engineering", "Marketing", "Sales"]
    for idx, ws in enumerate(workspaces):
        for month in range(3):
            generator.generate_invoice(
                vendor_name="Slack",
                amount=Decimal("80.00"),
                invoice_number=f"SLACK-{ws.upper()}-{month+1:02d}",
                invoice_date=base_date + timedelta(days=month * 30 + idx),
                line_items=[
                    {
                        "description": f"Slack Pro - {ws} Team",
                        "quantity": 10,
                        "unit_price": 8.00
                    }
                ],
                filename=f"04_subscription_sprawl_slack_{ws.lower()}_month{month+1}.pdf"
            )

    # ===== REGULAR SUBSCRIPTIONS (should NOT flag) =====
    print("\n5. REGULAR SUBSCRIPTIONS (should NOT be flagged as duplicates)")

    # Scenario 5A: Netflix monthly - consistent 30-day intervals
    for month in range(6):
        generator.generate_invoice(
            vendor_name="Netflix",
            amount=Decimal("15.99"),
            invoice_number=f"NFLX-{month+1:02d}-2024",
            invoice_date=base_date + timedelta(days=month * 30),
            filename=f"05_regular_subscription_netflix_month{month+1}.pdf"
        )

    # Scenario 5B: AWS monthly bills (varying amounts - normal)
    aws_amounts = [845.32, 923.17, 798.45, 1024.88, 867.92]
    for month, amount in enumerate(aws_amounts):
        generator.generate_invoice(
            vendor_name="Amazon Web Services",
            amount=Decimal(str(amount)),
            invoice_number=f"AWS-MONTHLY-{month+1:02d}",
            invoice_date=base_date + timedelta(days=month * 30 + 5),
            filename=f"05_regular_subscription_aws_month{month+1}.pdf"
        )

    # Scenario 5C: Annual renewal
    generator.generate_invoice(
        vendor_name="Adobe Creative Cloud",
        amount=Decimal("599.88"),
        invoice_number="ADOBE-2023-ANNUAL",
        invoice_date=base_date,
        filename="05_regular_subscription_adobe_year1.pdf"
    )
    generator.generate_invoice(
        vendor_name="Adobe Creative Cloud",
        amount=Decimal("599.88"),
        invoice_number="ADOBE-2024-ANNUAL",
        invoice_date=base_date + timedelta(days=365),
        filename="05_regular_subscription_adobe_year2.pdf"
    )

    # ===== EDGE CASES =====
    print("\n6. EDGE CASES (boundary testing)")

    # Scenario 6A: Just under price increase threshold (19% - should NOT flag)
    generator.generate_invoice(
        vendor_name="Asana",
        amount=Decimal("100.00"),
        invoice_number="ASANA-JAN",
        invoice_date=base_date + timedelta(days=0),
        filename="06_edge_case_asana_19pct_before.pdf"
    )
    generator.generate_invoice(
        vendor_name="Asana",
        amount=Decimal("119.00"),
        invoice_number="ASANA-FEB",
        invoice_date=base_date + timedelta(days=30),
        filename="06_edge_case_asana_19pct_after.pdf"
    )

    # Scenario 6B: Just over price increase threshold (21% - should flag)
    generator.generate_invoice(
        vendor_name="Monday.com",
        amount=Decimal("100.00"),
        invoice_number="MONDAY-JAN",
        invoice_date=base_date + timedelta(days=0),
        filename="06_edge_case_monday_21pct_before.pdf"
    )
    generator.generate_invoice(
        vendor_name="Monday.com",
        amount=Decimal("121.00"),
        invoice_number="MONDAY-FEB",
        invoice_date=base_date + timedelta(days=30),
        filename="06_edge_case_monday_21pct_after.pdf"
    )

    # Scenario 6C: Duplicate window boundary (7 days apart - should NOT flag as probable)
    generator.generate_invoice(
        vendor_name="Heroku",
        amount=Decimal("75.00"),
        invoice_number="HRK-001",
        invoice_date=base_date + timedelta(days=50),
        filename="06_edge_case_heroku_7days_first.pdf"
    )
    generator.generate_invoice(
        vendor_name="Heroku",
        amount=Decimal("75.00"),
        invoice_number="HRK-002",
        invoice_date=base_date + timedelta(days=57),
        filename="06_edge_case_heroku_7days_second.pdf"
    )

    print(f"\n=== Test invoice generation complete! ===")
    print(f"Total PDFs generated in: {generator.output_dir}/")
    print(f"\nTo use these:")
    print(f"1. Upload these PDFs to a test Gmail account")
    print(f"2. Run a scan through your application")
    print(f"3. Verify the detection results match expectations")


if __name__ == "__main__":
    generate_test_scenarios()
