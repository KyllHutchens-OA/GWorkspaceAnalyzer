"""
Authentication endpoints - Google OAuth flow
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta
import httpx

from ....config import settings
from ....core.security import create_access_token
from ....api.deps.auth import get_supabase_client, get_current_user
from supabase import Client

router = APIRouter()


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


class GoogleAuthRequest(BaseModel):
    """Google OAuth callback request"""
    code: str
    redirect_uri: Optional[str] = None


@router.get("/google/login")
async def google_login():
    """
    Initiate Google OAuth flow

    Returns redirect URL to Google OAuth consent screen
    """
    # Build Google OAuth URL
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile%20https://www.googleapis.com/auth/gmail.readonly&"
        f"access_type=offline&"
        f"prompt=consent"
    )

    return {"auth_url": auth_url}


@router.post("/google/callback", response_model=TokenResponse)
async def google_callback(
    auth_request: GoogleAuthRequest,
    supabase: Client = Depends(get_supabase_client),
):
    """
    Handle Google OAuth callback

    Exchanges authorization code for tokens, creates/updates user,
    and returns JWT access token

    Args:
        auth_request: Contains authorization code from Google
        supabase: Supabase client

    Returns:
        JWT access token for API authentication
    """
    try:
        # Exchange authorization code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": auth_request.code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": auth_request.redirect_uri or settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)

            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get tokens from Google: {token_response.text}",
                )

            tokens = token_response.json()
            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")

            # Get user info from Google
            userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}

            userinfo_response = await client.get(userinfo_url, headers=headers)

            if userinfo_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info from Google",
                )

            user_info = userinfo_response.json()
            email = user_info.get("email")
            google_id = user_info.get("id")

            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email not provided by Google",
                )

        # Check if user exists in Supabase
        existing_user = (
            supabase.table("users")
            .select("*")
            .eq("email", email)
            .execute()
        )

        if existing_user.data and len(existing_user.data) > 0:
            # Update existing user
            user = existing_user.data[0]
            user_id = user["id"]

            # TODO: Store refresh_token in Supabase Vault
            # For now, we'll skip token storage
            # In production, use: supabase.vault.create_secret(...)

        else:
            # Create new user
            # Note: In Supabase, users are created via Auth
            # This is a simplified version - in production, use Supabase Auth
            new_user_data = {
                "email": email,
                "preferences": {
                    "email_digest": True,
                    "alert_threshold": 1000,
                    "excluded_vendors": [],
                },
            }

            # This would fail with RLS - need to use Supabase Auth properly
            # For now, returning error to guide proper implementation
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="User creation requires Supabase Auth integration. "
                       "Please use Supabase client-side auth for new users.",
            )

        # Create JWT token for API access
        token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        jwt_token = create_access_token(
            data={"sub": user_id, "email": email},
            expires_delta=token_expires,
        )

        return TokenResponse(
            access_token=jwt_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"HTTP error during OAuth: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during authentication: {str(e)}",
        )


@router.post("/refresh")
async def refresh_token(
    current_user: dict = Depends(get_current_user),
):
    """
    Refresh access token

    Args:
        current_user: Current authenticated user

    Returns:
        New JWT access token
    """
    token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_token = create_access_token(
        data={"sub": current_user["id"], "email": current_user["email"]},
        expires_delta=token_expires,
    )

    return TokenResponse(
        access_token=new_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
):
    """
    Get current user information

    Args:
        current_user: Current authenticated user

    Returns:
        User profile data
    """
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "org_id": current_user.get("org_id"),
        "preferences": current_user.get("preferences", {}),
        "last_scan_at": current_user.get("last_scan_at"),
        "scan_count": current_user.get("scan_count", 0),
    }
