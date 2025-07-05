"""
User-related endpoints for the API.

This module provides FastAPI endpoints for user management in the authentication service.
Users are the primary entities that interact with applications, and this module supports:
- User registration with email, password, and optional metadata
- Retrieving user details by ID or email
- Updating user metadata and password
- User deletion with verification
"""

from app.routes.v1.schemas.user import UserLogin, UserLoginResponse
from app.utility.database import get_db
from app.utility.security import hash_email, verify_password
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=UserLoginResponse,
    response_description="User logged in successfully",
)
async def login_user(
    user: UserLogin, request: Request, db: AsyncSession = Depends(get_db)
):
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

    if not user_data or not verify_password(user.password, user_data.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserLoginResponse(user_id=user_data.id)
