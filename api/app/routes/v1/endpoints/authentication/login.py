"""
User-related endpoints for the API.

This module provides FastAPI endpoints for user management in the authentication service.
Users are the primary entities that interact with applications, and this module supports:
- User registration with email, password, and optional metadata
- Retrieving user details by ID or email
- Updating user metadata and password
- User deletion with verification
"""

from typing import Union

from app.utility.authentication import create_login_session, create_mfa_challenge_session
from app.utility.database import get_db
from app.utility.security import hash_email, verify_password
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.user import UserLogin2faResponse, UserLoginRequest, UserLoginResponse

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Union[UserLoginResponse, UserLogin2faResponse],
    response_description="User logged in successfully",
)
async def login_user(request_body: UserLoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Log in a user with email and password.

    This endpoint authenticates a user by verifying their email and password.
    If successful, it returns user details or sends to TOTP verification if required.

    Args:
        user: Request data containing the user's email and password
        db: Database session dependency

    Returns:
        Union[UserLoginResponse, UserLogin2faResponse]: Response containing user details upon successful login.
        Returns UserLogin2faResponse if 2FA is enabled, UserLoginResponse otherwise.

    Raises:
        HTTPException: If authentication fails or user is not found
    """

    # Define error mappings for cleaner exception handling
    error_mappings = {
        "User not found with specified email": (
            status.HTTP_401_UNAUTHORIZED,
            "Invalid credentials",
        ),
        "Invalid password": (
            status.HTTP_401_UNAUTHORIZED,
            "Invalid credentials",
        ),
        "User is suspended": (
            status.HTTP_403_FORBIDDEN,
            "User account is suspended",
        ),
    }

    try:
        result = await db.execute(
            text(
                """
                SELECT * FROM login_user (
                    p_app_id => :app_id,
                    p_email_hash => :email_hash,
                    p_ip_address => :ip_address,
                    p_user_agent => :user_agent
                )"""
            ),
            {
                "app_id": request_body.app_id,
                "email_hash": hash_email(request_body.email, request_body.app_id),
                "ip_address": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent", ""),
            },
        )
        data = result.fetchone()

        if not data:
            raise ValueError("User not found with specified email")

        if not verify_password(request_body.password, data.password_hash):
            raise ValueError("Invalid password")

        # Convert to response model for adding tokens
        user_dict = dict(data._mapping) if hasattr(data, "_mapping") else dict(data)

        if data.is_2fa_enabled:
            mfa_access_token = await create_mfa_challenge_session(data.id, db, request_body.app_id, request)
            user_dict.update({"challenge_token": mfa_access_token})
            return UserLogin2faResponse.model_validate(user_dict)

        # Create session and refresh tokens for the opaque token flow
        access_token, refresh_token = await create_login_session(data.id, db, request_body.app_id, request)
        user_dict.update({"access_token": access_token, "refresh_token": refresh_token})
        return UserLoginResponse.model_validate(user_dict)

    except Exception as e:
        error_str = str(e)

        # Check for known database errors
        for error_msg, (status_code, detail) in error_mappings.items():
            if error_msg in error_str:
                raise HTTPException(status_code=status_code, detail=detail)

        # Re-raise unknown exceptions
        raise
