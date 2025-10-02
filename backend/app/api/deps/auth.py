"""
Authentication dependencies for FastAPI
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import jwt

from ...config import settings

security = HTTPBearer()

DEV_TOKEN = "dev-token-12345-abcde"
DEV_USER = {
    "id": "00000000-0000-0000-0000-000000000001",
    "email": "dev@example.com",
    "name": "Development User",
    "created_at": "2025-01-01T00:00:00Z",
}


def get_supabase_client() -> Optional[Client]:
    """Get Supabase client instance"""
    if settings.DEBUG and not settings.SUPABASE_URL:
        return None

    try:
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    except TypeError as e:
        if "proxy" in str(e):
            if settings.DEBUG:
                return None
        raise


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Optional[Client] = Depends(get_supabase_client),
) -> dict:
    """
    Get current authenticated user from Supabase JWT token

    Args:
        credentials: Bearer token from Authorization header
        supabase: Supabase client

    Returns:
        User data dictionary

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    if settings.DEBUG and token == DEV_TOKEN:
        return DEV_USER

    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not configured",
        )

    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
            options={"verify_exp": True, "verify_iat": False},  # Disable IAT verification for clock skew
        )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        result = supabase.table("users").select("*").eq("id", user_id).execute()

        if not result.data or len(result.data) == 0:
            new_user_data = {
                "id": user_id,
                "email": payload.get("email"),
                "org_id": None,
                "preferences": {
                    "email_digest": True,
                    "alert_threshold": 1000,
                    "excluded_vendors": [],
                },
            }

            insert_result = supabase.table("users").insert(new_user_data).execute()

            if not insert_result.data or len(insert_result.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user",
                )

            return insert_result.data[0]

        return result.data[0]

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    supabase: Client = Depends(get_supabase_client),
) -> Optional[dict]:
    """
    Get current user if authenticated, otherwise None

    Useful for endpoints that work with or without authentication
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials, supabase)
    except HTTPException:
        return None
