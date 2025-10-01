"""
Development endpoints for testing and seeding data
Only available in development mode
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime, timedelta, date
from uuid import uuid4
import random

from ....api.deps.auth import get_current_user, get_supabase_client
from ....config import settings
from supabase import Client
from typing import Optional

router = APIRouter()


class SeedDataResponse(BaseModel):
    """Response from seed data operation"""
    message: str
    invoices_created: int
    findings_created: int
    scan_jobs_created: int


def generate_sample_invoices(user_id: str, org_id: str, scan_job_id: str) -> List[Dict[str, Any]]:
    """Generate sample invoice data for testing"""
    vendors = [
        ("AWS", 1500, 3500),
        ("Google Workspace", 400, 800),
        ("Stripe", 200, 500),
        ("Slack", 300, 600),
        ("Zoom", 250, 450),
        ("Notion", 50, 150),
        ("GitHub", 100, 300),
        ("Vercel", 150, 400),
        ("MongoDB Atlas", 200, 600),
        ("SendGrid", 50, 200),
    ]

    invoices = []
    base_date = datetime.now() - timedelta(days=90)

    for vendor_name, min_amount, max_amount in vendors:
        # Generate 3-8 invoices per vendor over 90 days
        num_invoices = random.randint(3, 8)

        for i in range(num_invoices):
            amount = random.uniform(min_amount, max_amount)
            invoice_date = base_date + timedelta(days=random.randint(0, 90))

            # Create some duplicates (same amount within 7 days)
            if random.random() < 0.15:  # 15% chance of duplicate
                duplicate_date = invoice_date + timedelta(days=random.randint(1, 7))
                invoices.append({
                    "org_id": org_id,
                    "user_id": user_id,
                    "scan_job_id": scan_job_id,
                    "gmail_message_id": f"msg_{uuid4().hex[:16]}",
                    "gmail_thread_id": f"thread_{uuid4().hex[:16]}",
                    "vendor_name": vendor_name,
                    "amount": round(amount, 2),
                    "currency": "USD",
                    "invoice_number": f"INV-{random.randint(10000, 99999)}",
                    "invoice_date": duplicate_date.date().isoformat(),
                    "due_date": (duplicate_date + timedelta(days=30)).date().isoformat(),
                    "extraction_method": "pdf_parser",
                    "confidence_score": 0.95,
                })

            invoices.append({
                "org_id": org_id,
                "user_id": user_id,
                "scan_job_id": scan_job_id,
                "gmail_message_id": f"msg_{uuid4().hex[:16]}",
                "gmail_thread_id": f"thread_{uuid4().hex[:16]}",
                "vendor_name": vendor_name,
                "amount": round(amount, 2),
                "currency": "USD",
                "invoice_number": f"INV-{random.randint(10000, 99999)}",
                "invoice_date": invoice_date.date().isoformat(),
                "due_date": (invoice_date + timedelta(days=30)).date().isoformat(),
                "extraction_method": "pdf_parser",
                "confidence_score": random.uniform(0.85, 1.0),
            })

    return invoices


def generate_sample_findings(org_id: str, invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate sample findings based on invoices"""
    findings = []

    # Group invoices by vendor
    by_vendor: Dict[str, List[Dict[str, Any]]] = {}
    for invoice in invoices:
        vendor = invoice["vendor_name"]
        if vendor not in by_vendor:
            by_vendor[vendor] = []
        by_vendor[vendor].append(invoice)

    # Detect duplicates
    for vendor, vendor_invoices in by_vendor.items():
        vendor_invoices.sort(key=lambda x: x["invoice_date"])

        for i, invoice in enumerate(vendor_invoices):
            # Check for duplicates within 7 days
            for other in vendor_invoices[i+1:]:
                days_diff = (
                    datetime.fromisoformat(other["invoice_date"]) -
                    datetime.fromisoformat(invoice["invoice_date"])
                ).days

                if days_diff <= 7 and abs(invoice["amount"] - other["amount"]) < 1:
                    findings.append({
                        "org_id": org_id,
                        "type": "duplicate",
                        "status": "pending",
                        "amount": invoice["amount"],
                        "currency": "USD",
                        "title": f"Duplicate charge from {vendor}",
                        "description": f"Invoice charged twice within {days_diff} days: ${invoice['amount']:.2f}",
                        "confidence_score": 0.95,
                        "details": {
                            "vendor": vendor,
                            "invoice_numbers": [invoice["invoice_number"], other["invoice_number"]],
                            "dates": [invoice["invoice_date"], other["invoice_date"]],
                        },
                    })

    # Generate subscription sprawl findings
    sprawl_vendors = ["Slack", "Zoom", "Notion"]
    for vendor in sprawl_vendors:
        if vendor in by_vendor and len(by_vendor[vendor]) >= 3:
            potential_savings = sum(inv["amount"] for inv in by_vendor[vendor][:2]) * 0.5
            findings.append({
                "org_id": org_id,
                "type": "unused_subscription",
                "status": "pending",
                "amount": potential_savings,
                "currency": "USD",
                "title": f"Multiple {vendor} subscriptions detected",
                "description": f"Found {len(by_vendor[vendor])} separate {vendor} charges - potential consolidation opportunity",
                "confidence_score": 0.85,
                "details": {
                    "vendor": vendor,
                    "subscription_count": len(by_vendor[vendor]),
                    "total_monthly_cost": sum(inv["amount"] for inv in by_vendor[vendor]),
                },
            })

    # Generate price increase findings
    for vendor, vendor_invoices in by_vendor.items():
        if len(vendor_invoices) >= 3:
            recent = vendor_invoices[-1]["amount"]
            old = vendor_invoices[0]["amount"]

            if recent > old * 1.2:  # 20% increase
                increase_pct = ((recent - old) / old) * 100
                findings.append({
                    "org_id": org_id,
                    "type": "price_increase",
                    "status": "pending",
                    "amount": recent - old,
                    "currency": "USD",
                    "title": f"{vendor} price increased by {increase_pct:.0f}%",
                    "description": f"Price increased from ${old:.2f} to ${recent:.2f}",
                    "confidence_score": 0.90,
                    "details": {
                        "vendor": vendor,
                        "old_price": old,
                        "new_price": recent,
                        "increase_percent": increase_pct,
                    },
                })

    return findings


@router.post("/seed", response_model=SeedDataResponse)
async def seed_development_data(
    current_user: dict = Depends(get_current_user),
    supabase: Optional[Client] = Depends(get_supabase_client),
):
    """
    Seed development data for testing

    Creates:
    - A completed scan job
    - 30-50 sample invoices across 10 vendors
    - 5-15 findings (duplicates, subscription sprawl, price increases)

    Only available in development mode
    """
    # Only allow in development
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seed endpoint only available in development mode"
        )

    # Check if Supabase is configured
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Database not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables."
        )

    user_id = current_user["id"]

    # Create or get org
    try:
        existing_org = supabase.table("organizations").select("id").eq("name", "Dev Organization").execute()
        if not existing_org.data:
            org_result = supabase.table("organizations").insert({
                "name": "Dev Organization",
                "google_domain": "dev.example.com",
                "subscription_tier": "pro",
            }).execute()
            org_id = org_result.data[0]["id"]
            print(f"Created dev org: {org_id}")
        else:
            org_id = existing_org.data[0]["id"]
            print(f"Dev org already exists: {org_id}")
    except Exception as e:
        print(f"Error checking/creating org: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create dev org: {str(e)}"
        )

    # Ensure dev user exists in Supabase Auth and our users table
    # Note: In dev mode, we bypass RLS by using service role key
    try:
        # First try to check if auth user exists, if not create it
        auth_user_exists = False
        try:
            auth_user_response = supabase.auth.admin.get_user_by_id(user_id)
            if auth_user_response.user:
                auth_user_exists = True
                print(f"Auth user already exists: {user_id}")
        except Exception as check_error:
            print(f"Auth user does not exist: {check_error}")

        if not auth_user_exists:
            # Create user in Supabase Auth with the specific UUID
            auth_result = supabase.auth.admin.create_user({
                "email": current_user.get("email", "dev@example.com"),
                "password": "dev-password-not-used",
                "email_confirm": True,
                "user_metadata": {
                    "name": current_user.get("name", "Development User"),
                    "id": user_id,
                }
            })
            print(f"Created auth user: {auth_result.user.id}")
            actual_user_id = auth_result.user.id
        else:
            actual_user_id = user_id

        # Now check/create in our users table
        existing_user = supabase.table("users").select("id").eq("id", actual_user_id).execute()
        if not existing_user.data:
            user_result = supabase.table("users").insert({
                "id": actual_user_id,
                "email": current_user.get("email", "dev@example.com"),
                "org_id": org_id,
            }).execute()
            print(f"Created user in users table: {user_result.data}")
        else:
            print(f"User already exists in users table: {existing_user.data}")
            # Update org_id if needed
            if not existing_user.data[0].get("org_id"):
                supabase.table("users").update({"org_id": org_id}).eq("id", actual_user_id).execute()

        # Use the actual user ID for subsequent operations
        user_id = actual_user_id

    except Exception as e:
        print(f"Error checking/creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create dev user: {str(e)}"
        )

    # Create a completed scan job
    scan_job_data = {
        "user_id": user_id,
        "org_id": org_id,
        "status": "completed",
        "start_date": (date.today() - timedelta(days=90)).isoformat(),
        "end_date": date.today().isoformat(),
        "total_emails": 127,
        "processed_emails": 127,
        "invoices_found": 0,  # Will update after inserting
        "started_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        "completed_at": (datetime.now() - timedelta(hours=1, minutes=45)).isoformat(),
    }

    scan_result = supabase.table("scan_jobs").insert(scan_job_data).execute()
    scan_job = scan_result.data[0]
    scan_job_id = scan_job["id"]

    # Generate and insert invoices
    invoices = generate_sample_invoices(user_id, org_id, scan_job_id)
    invoice_result = supabase.table("invoices").insert(invoices).execute()
    invoices_created = len(invoice_result.data)

    # Update scan job with invoice count
    supabase.table("scan_jobs").update({
        "invoices_found": invoices_created
    }).eq("id", scan_job_id).execute()

    # Generate and insert findings
    findings = generate_sample_findings(org_id, invoices)
    findings_result = supabase.table("findings").insert(findings).execute()
    findings_created = len(findings_result.data)

    return SeedDataResponse(
        message=f"Successfully seeded development data for user {user_id}",
        invoices_created=invoices_created,
        findings_created=findings_created,
        scan_jobs_created=1,
    )


@router.post("/clear")
async def clear_development_data(
    current_user: dict = Depends(get_current_user),
    supabase: Optional[Client] = Depends(get_supabase_client),
):
    """
    Clear all user data for testing

    Deletes:
    - All scan jobs
    - All invoices
    - All findings

    Only available in development mode
    """
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clear endpoint only available in development mode"
        )

    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Database not configured"
        )

    user_id = current_user["id"]

    # Delete in order (foreign key constraints)
    supabase.table("findings").delete().eq("user_id", user_id).execute()
    supabase.table("invoices").delete().eq("user_id", user_id).execute()
    supabase.table("scan_jobs").delete().eq("user_id", user_id).execute()

    return {"message": f"All data cleared for user {user_id}"}
