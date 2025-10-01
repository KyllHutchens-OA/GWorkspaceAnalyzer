"""
Scan job endpoints - Trigger and monitor Gmail scans
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date, timedelta
from uuid import UUID

from ....api.deps.auth import get_current_user, get_supabase_client
from ....services.scan_processor import process_scan_job
from supabase import Client

router = APIRouter()


class ScanJobCreate(BaseModel):
    """Request to create a new scan job"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2024-01-01",
                "end_date": "2024-03-31",
            }
        }


class ScanJobResponse(BaseModel):
    """Scan job details"""
    id: str
    user_id: str
    org_id: Optional[str]
    status: str
    start_date: date
    end_date: date
    total_emails: int
    processed_emails: int
    invoices_found: int
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime


@router.post("/start", response_model=ScanJobResponse, status_code=status.HTTP_201_CREATED)
async def start_scan(
    scan_request: ScanJobCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Start a new Gmail scan job

    Creates a scan job in the database and triggers background processing

    Args:
        scan_request: Scan parameters (date range)
        background_tasks: FastAPI background tasks
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        Created scan job details
    """
    # Default date range: last 90 days
    end_date = scan_request.end_date or date.today()
    start_date = scan_request.start_date or (end_date - timedelta(days=90))

    # Validate date range
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before end_date",
        )

    # Check for existing active scans
    existing_scans = (
        supabase.table("scan_jobs")
        .select("*")
        .eq("user_id", current_user["id"])
        .in_("status", ["queued", "processing"])
        .execute()
    )

    if existing_scans.data and len(existing_scans.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A scan is already in progress. Please wait for it to complete.",
        )

    # Create scan job
    scan_job_data = {
        "user_id": current_user["id"],
        "org_id": current_user.get("org_id"),
        "status": "queued",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_emails": 0,
        "processed_emails": 0,
        "invoices_found": 0,
    }

    result = supabase.table("scan_jobs").insert(scan_job_data).execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create scan job",
        )

    scan_job = result.data[0]

    # Add background task to process scan
    background_tasks.add_task(process_scan_job, scan_job["id"], current_user, supabase)

    return ScanJobResponse(**scan_job)


@router.get("/jobs", response_model=List[ScanJobResponse])
async def list_scan_jobs(
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    List user's scan jobs

    Args:
        limit: Maximum number of jobs to return
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        List of scan jobs ordered by creation date
    """
    result = (
        supabase.table("scan_jobs")
        .select("*")
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return [ScanJobResponse(**job) for job in result.data]


@router.get("/jobs/{job_id}", response_model=ScanJobResponse)
async def get_scan_job(
    job_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Get scan job details

    Args:
        job_id: Scan job ID
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        Scan job details
    """
    result = (
        supabase.table("scan_jobs")
        .select("*")
        .eq("id", str(job_id))
        .eq("user_id", current_user["id"])
        .execute()
    )

    if not result.data or len(result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan job not found",
        )

    return ScanJobResponse(**result.data[0])


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_scan_job(
    job_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Cancel a queued or processing scan job

    Args:
        job_id: Scan job ID
        current_user: Authenticated user
        supabase: Supabase client
    """
    # Get job
    result = (
        supabase.table("scan_jobs")
        .select("*")
        .eq("id", str(job_id))
        .eq("user_id", current_user["id"])
        .execute()
    )

    if not result.data or len(result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan job not found",
        )

    job = result.data[0]

    # Can only cancel queued or processing jobs
    if job["status"] not in ["queued", "processing"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status: {job['status']}",
        )

    # Update status to failed with cancellation message
    supabase.table("scan_jobs").update({
        "status": "failed",
        "error_message": "Cancelled by user",
        "completed_at": datetime.utcnow().isoformat(),
    }).eq("id", str(job_id)).execute()

    return None
