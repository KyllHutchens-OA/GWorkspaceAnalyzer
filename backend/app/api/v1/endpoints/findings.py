"""
Findings endpoints - Manage detected issues (duplicates, price increases, etc.)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from ....api.deps.auth import get_current_user, get_supabase_client
from supabase import Client

router = APIRouter()


class FindingResponse(BaseModel):
    """Finding details"""
    id: str
    org_id: Optional[str]
    type: str
    status: str
    title: str
    description: Optional[str]
    amount: Decimal
    currency: str
    confidence_score: Optional[Decimal]
    details: Optional[dict]
    created_at: datetime
    resolved_by: Optional[str]
    resolved_at: Optional[datetime]
    user_notes: Optional[str]


class FindingListResponse(BaseModel):
    """Paginated findings list"""
    findings: List[FindingResponse]
    total: int
    page: int
    page_size: int


class FindingSummary(BaseModel):
    """Summary of findings by type and status"""
    pending_count: int
    resolved_count: int
    ignored_count: int
    total_guaranteed_waste: Decimal
    total_potential_waste: Decimal
    by_type: dict


class UpdateFindingRequest(BaseModel):
    """Request to update finding status"""
    status: str  # 'resolved', 'ignored'
    user_notes: Optional[str] = None


@router.get("/summary", response_model=FindingSummary)
async def get_findings_summary(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Get summary of findings

    Returns counts and totals by type and status

    Args:
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        Findings summary with waste calculations
    """
    query = supabase.table("findings").select("*")

    if current_user.get("org_id"):
        query = query.eq("org_id", current_user["org_id"])

    result = query.execute()
    findings = result.data

    # Calculate stats
    pending_count = sum(1 for f in findings if f.get("status") == "pending")
    resolved_count = sum(1 for f in findings if f.get("status") == "resolved")
    ignored_count = sum(1 for f in findings if f.get("status") == "ignored")

    # Calculate guaranteed waste (only exact duplicates and price increases)
    guaranteed_waste = Decimal("0.00")
    potential_waste = Decimal("0.00")

    for finding in findings:
        if finding.get("status") == "pending":
            amount = Decimal(str(finding.get("amount", 0)))

            # Guaranteed waste: exact duplicates and price increases
            if finding.get("type") in ["duplicate", "price_increase"]:
                # Check if it's an exact duplicate (high confidence)
                details = finding.get("details", {})
                if finding.get("type") == "duplicate":
                    # Exact duplicates have amount > 0
                    # Probable duplicates have amount = 0
                    if amount > 0:
                        guaranteed_waste += amount
                    else:
                        # This is a probable duplicate (review flag)
                        potential_waste += Decimal(str(details.get("potential_waste", 0)))
                else:
                    # Price increases always count
                    guaranteed_waste += amount

    # Group by type
    by_type = {}
    for finding in findings:
        f_type = finding.get("type", "unknown")
        if f_type not in by_type:
            by_type[f_type] = {"count": 0, "pending": 0, "total_amount": 0.0}

        by_type[f_type]["count"] += 1
        if finding.get("status") == "pending":
            by_type[f_type]["pending"] += 1
            by_type[f_type]["total_amount"] += float(finding.get("amount", 0))

    return FindingSummary(
        pending_count=pending_count,
        resolved_count=resolved_count,
        ignored_count=ignored_count,
        total_guaranteed_waste=guaranteed_waste,
        total_potential_waste=potential_waste,
        by_type=by_type,
    )


@router.get("", response_model=FindingListResponse)
async def list_findings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    List findings with filters and pagination

    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        status: Filter by status (pending, resolved, ignored)
        type: Filter by type (duplicate, price_increase, etc.)
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        Paginated list of findings
    """
    query = supabase.table("findings").select("*", count="exact")

    # Filter by organization
    if current_user.get("org_id"):
        query = query.eq("org_id", current_user["org_id"])

    # Apply filters
    if status:
        query = query.eq("status", status)

    if type:
        query = query.eq("type", type)

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order("created_at", desc=True).range(offset, offset + page_size - 1)

    # Execute query
    result = query.execute()

    total = result.count if result.count is not None else 0
    findings = [FindingResponse(**f) for f in result.data]

    return FindingListResponse(
        findings=findings,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{finding_id}", response_model=FindingResponse)
async def get_finding(
    finding_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Get single finding by ID with related invoice details

    Args:
        finding_id: Finding ID
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        Finding details
    """
    query = supabase.table("findings").select("*").eq("id", str(finding_id))

    if current_user.get("org_id"):
        query = query.eq("org_id", current_user["org_id"])

    result = query.execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )

    return FindingResponse(**result.data[0])


@router.get("/{finding_id}/invoices")
async def get_finding_invoices(
    finding_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Get invoices related to a finding

    Args:
        finding_id: Finding ID
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        List of related invoices
    """
    # Get finding_invoices junction records
    junction_result = (
        supabase.table("finding_invoices")
        .select("invoice_id")
        .eq("finding_id", str(finding_id))
        .execute()
    )

    if not junction_result.data:
        return []

    invoice_ids = [record["invoice_id"] for record in junction_result.data]

    # Get invoice details
    invoices_result = (
        supabase.table("invoices")
        .select("*")
        .in_("id", invoice_ids)
        .execute()
    )

    return invoices_result.data


@router.patch("/{finding_id}", response_model=FindingResponse)
async def update_finding(
    finding_id: UUID,
    update_request: UpdateFindingRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Update finding status (resolve or ignore)

    Args:
        finding_id: Finding ID
        update_request: Status update and notes
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        Updated finding
    """
    # Verify finding exists and user has access
    query = supabase.table("findings").select("*").eq("id", str(finding_id))

    if current_user.get("org_id"):
        query = query.eq("org_id", current_user["org_id"])

    result = query.execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )

    # Validate status
    if update_request.status not in ["resolved", "ignored", "pending"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'resolved', 'ignored', or 'pending'",
        )

    # Update finding
    update_data = {
        "status": update_request.status,
        "updated_at": datetime.utcnow().isoformat(),
    }

    if update_request.status in ["resolved", "ignored"]:
        update_data["resolved_by"] = current_user["id"]
        update_data["resolved_at"] = datetime.utcnow().isoformat()

    if update_request.user_notes:
        update_data["user_notes"] = update_request.user_notes

    updated_result = (
        supabase.table("findings")
        .update(update_data)
        .eq("id", str(finding_id))
        .execute()
    )

    if not updated_result.data or len(updated_result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update finding",
        )

    # Log action in audit_log
    audit_data = {
        "user_id": current_user["id"],
        "org_id": current_user.get("org_id"),
        "action": f"finding_{update_request.status}",
        "entity_type": "finding",
        "entity_id": str(finding_id),
        "changes": {
            "status": {"from": result.data[0].get("status"), "to": update_request.status}
        },
        "metadata": {"user_notes": update_request.user_notes} if update_request.user_notes else {},
    }

    supabase.table("audit_log").insert(audit_data).execute()

    return FindingResponse(**updated_result.data[0])


@router.delete("/{finding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_finding(
    finding_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Delete a finding (admin only, typically findings are just marked as resolved/ignored)

    Args:
        finding_id: Finding ID
        current_user: Authenticated user
        supabase: Supabase client
    """
    # Verify ownership
    query = supabase.table("findings").select("id").eq("id", str(finding_id))

    if current_user.get("org_id"):
        query = query.eq("org_id", current_user["org_id"])

    result = query.execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )

    # Delete finding
    supabase.table("findings").delete().eq("id", str(finding_id)).execute()

    return None
