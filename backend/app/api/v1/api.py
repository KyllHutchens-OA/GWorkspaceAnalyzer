"""
API v1 router - Combines all endpoint routers
"""
from fastapi import APIRouter

from .endpoints import auth, scan, invoices, findings, dev, subscription

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Subscription & billing
api_router.include_router(subscription.router, prefix="/subscription", tags=["subscription"])

# Scan jobs
api_router.include_router(scan.router, prefix="/scan", tags=["scan"])

# Invoices
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])

# Findings
api_router.include_router(findings.router, prefix="/findings", tags=["findings"])

# Development (only enabled in DEBUG mode)
api_router.include_router(dev.router, prefix="/dev", tags=["development"])
