"""
User-related endpoints for the API.

This module provides FastAPI endpoints for user management in the authentication service.
Users are the primary entities that interact with applications, and this module supports:
- User registration with email, password, and optional metadata
- Retrieving user details by ID or email
- Updating user metadata and password
- User deletion with verification
"""

from app.routes.v1.schemas.user import UserLogin, UserLogin2faResponse, UserLoginResponse
from app.utility.database import get_db
from app.utility.security import create_token, hash_email, verify_password
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


async def create_and_return_session(user_id: int, db: AsyncSession, app_id: int, request: Request):
    """
    Create a session for the user and return session details.

    This function creates a session for the authenticated user and returns the session details.
    It is used after successful user login.

    Args:
        user_id: The ID of the user for whom the session is being created
        db: Database session dependency
        app_id: The ID of the application for which the session is created
        request: The HTTP request object to extract client information

    Returns:
        dict: A dictionary containing session details including access and refresh tokens
    """
    session_token = create_token()
    refresh_token = create_token()

    return session_token, refresh_token


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=UserLoginResponse,
    response_description="User logged in successfully",
)
async def login_user(user: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Log in a user with email and password.

    This endpoint authenticates a user by verifying their email and password.
    If successful, it returns user details or sends to TOTP verification if required.

    Args:
        user: Request data containing the user's email and password
        db: Database session dependency

    Returns:
        UserLoginResponse: Response containing user details upon successful login

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
                "app_id": user.app_id,
                "email_hash": hash_email(user.email),
                "ip_address": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent", ""),
            },
        )
        user_data = result.fetchone()

        if not user_data:
            raise ValueError("User not found with specified email")

        if not verify_password(user.password, user_data.password_hash):
            raise ValueError("Invalid password")

        if user_data.is_2fa_enabled:
            return UserLogin2faResponse.model_validate(user_data)

        # Create session and refresh tokens for the opaque token flow
        session_token, refresh_token = await create_and_return_session(user_data.id, db, user.app_id, request)

        # Convert to response model by adding tokens to user data
        user_dict = dict(user_data._mapping) if hasattr(user_data, "_mapping") else dict(user_data)
        user_dict.update({"session_token": session_token, "refresh_token": refresh_token})

        return UserLoginResponse.model_validate(user_dict)

    except Exception as e:
        error_str = str(e)

        # Check for known database errors
        for error_msg, (status_code, detail) in error_mappings.items():
            if error_msg in error_str:
                raise HTTPException(status_code=status_code, detail=detail)

        # Re-raise unknown exceptions
        raise
