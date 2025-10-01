"""
Invoice endpoints - CRUD operations for invoices
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from uuid import UUID
from decimal import Decimal

from ....api.deps.auth import get_current_user, get_supabase_client
from supabase import Client

router = APIRouter()


class InvoiceResponse(BaseModel):
    """Invoice details"""
    id: str
    org_id: Optional[str]
    user_id: Optional[str]
    gmail_message_id: str
    vendor_name: str
    vendor_name_normalized: Optional[str]
    invoice_number: Optional[str]
    amount: Decimal
    currency: str
    invoice_date: Optional[date]
    due_date: Optional[date]
    confidence_score: Optional[Decimal]
    extraction_method: Optional[str]
    processed_at: Optional[date]


class InvoiceListResponse(BaseModel):
    """Paginated invoice list"""
    invoices: List[InvoiceResponse]
    total: int
    page: int
    page_size: int


@router.get("", response_model=InvoiceListResponse)
async def list_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    vendor: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    List invoices with filters and pagination

    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        vendor: Filter by vendor name (normalized)
        start_date: Filter by invoice date >= start_date
        end_date: Filter by invoice date <= end_date
        min_amount: Filter by amount >= min_amount
        max_amount: Filter by amount <= max_amount
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        Paginated list of invoices
    """
    # Build query
    query = supabase.table("invoices").select("*", count="exact")

    # Filter by organization
    if current_user.get("org_id"):
        query = query.eq("org_id", current_user["org_id"])
    else:
        # If no org, filter by user
        query = query.eq("user_id", current_user["id"])

    # Apply filters
    if vendor:
        query = query.ilike("vendor_name_normalized", f"%{vendor}%")

    if start_date:
        query = query.gte("invoice_date", start_date.isoformat())

    if end_date:
        query = query.lte("invoice_date", end_date.isoformat())

    if min_amount is not None:
        query = query.gte("amount", float(min_amount))

    if max_amount is not None:
        query = query.lte("amount", float(max_amount))

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order("invoice_date", desc=True).range(offset, offset + page_size - 1)

    # Execute query
    result = query.execute()

    total = result.count if result.count is not None else 0
    invoices = [InvoiceResponse(**inv) for inv in result.data]

    return InvoiceListResponse(
        invoices=invoices,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Get single invoice by ID

    Args:
        invoice_id: Invoice ID
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        Invoice details
    """
    query = supabase.table("invoices").select("*").eq("id", str(invoice_id))

    # Filter by organization or user
    if current_user.get("org_id"):
        query = query.eq("org_id", current_user["org_id"])
    else:
        query = query.eq("user_id", current_user["id"])

    result = query.execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    return InvoiceResponse(**result.data[0])


@router.get("/vendors/list")
async def list_vendors(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Get unique list of vendors from invoices

    Returns list of vendor names with invoice counts and total amounts

    Args:
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        List of vendors with aggregated data
    """
    # This would ideally use a SQL aggregate query
    # For now, we'll fetch from the vendors table if it exists
    # Or aggregate in Python

    query = supabase.table("vendors").select("*")

    if current_user.get("org_id"):
        query = query.eq("org_id", current_user["org_id"])

    result = query.order("total_spent", desc=True).execute()

    return result.data


@router.get("/stats/summary")
async def get_invoice_stats(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Get invoice statistics summary

    Returns aggregated stats like total invoices, total amount, etc.

    Args:
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        Statistics summary
    """
    # Fetch all invoices for stats calculation
    query = supabase.table("invoices").select("amount, invoice_date")

    if current_user.get("org_id"):
        query = query.eq("org_id", current_user["org_id"])
    else:
        query = query.eq("user_id", current_user["id"])

    result = query.execute()

    invoices = result.data

    # Calculate stats
    total_invoices = len(invoices)
    total_amount = sum(Decimal(str(inv.get("amount", 0))) for inv in invoices)

    # Group by month
    monthly_totals = {}
    for inv in invoices:
        if inv.get("invoice_date"):
            month_key = inv["invoice_date"][:7]  # YYYY-MM
            monthly_totals[month_key] = monthly_totals.get(month_key, Decimal("0")) + Decimal(
                str(inv.get("amount", 0))
            )

    return {
        "total_invoices": total_invoices,
        "total_amount": float(total_amount),
        "currency": "USD",
        "monthly_totals": {k: float(v) for k, v in monthly_totals.items()},
    }


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Delete an invoice

    Args:
        invoice_id: Invoice ID
        current_user: Authenticated user
        supabase: Supabase client
    """
    # Verify ownership
    query = supabase.table("invoices").select("id").eq("id", str(invoice_id))

    if current_user.get("org_id"):
        query = query.eq("org_id", current_user["org_id"])
    else:
        query = query.eq("user_id", current_user["id"])

    result = query.execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    # Delete invoice
    supabase.table("invoices").delete().eq("id", str(invoice_id)).execute()

    return None
