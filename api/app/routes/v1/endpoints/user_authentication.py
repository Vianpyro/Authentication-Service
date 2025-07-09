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

from app.utility.database import get_db
from app.utility.security import create_token, hash_email, hash_token, verify_password
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.totp_secret import TOTPSecretChallengeRequest
from ..schemas.user import UserLogin2faResponse, UserLoginRequest, UserLoginResponse

router = APIRouter()


async def create_login_session(user_id: int, db: AsyncSession, app_id: int, request: Request):
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
    access_token = create_token()
    refresh_token = create_token()

    await db.execute(
        text(
            """
            CALL create_session (
                p_app_id => :app_id,
                p_user_id => :user_id,
                p_access_token_hash => :access_token,
                p_refresh_token_hash => :refresh_token,
                p_ip_address => :ip_address,
                p_user_agent => :user_agent
            )"""
        ),
        {
            "app_id": app_id,
            "user_id": user_id,
            "access_token": hash_token(access_token),
            "refresh_token": hash_token(refresh_token),
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent", ""),
        },
    )
    await db.commit()

    return access_token, refresh_token


async def create_mfa_challenge_session(user_id: int, db: AsyncSession, app_id: int, request: Request):
    """
    Create a multi-factor authentication (MFA) challenge session for the user.

    This function initiates an MFA challenge session for the user and returns the challenge token.

    Args:
        user_id: The ID of the user for whom the MFA challenge is being created
        db: Database session dependency
        app_id: The ID of the application for which the MFA challenge is created
        request: The HTTP request object to extract client information

    Returns:
        str: The challenge token for the MFA session
    """
    challenge_token = create_token()

    await db.execute(
        text(
            """
            CALL create_mfa_challenge_session (
                p_app_id => :app_id,
                p_user_id => :user_id,
                p_challenge_token_hash => :challenge_token_hash,
                p_ip_address => :ip_address,
                p_user_agent => :user_agent
            )"""
        ),
        {
            "app_id": app_id,
            "user_id": user_id,
            "challenge_token_hash": hash_token(challenge_token),
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent", ""),
        },
    )

    return challenge_token


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=Union[UserLoginResponse, UserLogin2faResponse],
    response_description="User logged in successfully",
)
async def login_user(user: UserLoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
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
                "app_id": user.app_id,
                "email_hash": hash_email(user.email, user.app_id),
                "ip_address": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent", ""),
            },
        )
        data = result.fetchone()

        if not data:
            raise ValueError("User not found with specified email")

        if not verify_password(user.password, data.password_hash):
            raise ValueError("Invalid password")

        # Convert to response model for adding tokens
        user_dict = dict(data._mapping) if hasattr(data, "_mapping") else dict(data)

        if data.is_2fa_enabled:
            mfa_access_token = await create_mfa_challenge_session(data.id, db, user.app_id, request)
            user_dict.update({"challenge_token": mfa_access_token})
            return UserLogin2faResponse.model_validate(user_dict)

        # Create session and refresh tokens for the opaque token flow
        access_token, refresh_token = await create_login_session(data.id, db, user.app_id, request)
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


@router.post(
    "/challenge",
    status_code=status.HTTP_200_OK,
    response_model=UserLoginResponse,
    response_description="User confirmed 2FA successfully",
)
async def confirm_2fa(totp: TOTPSecretChallengeRequest, db: AsyncSession = Depends(get_db)):
    """
    Confirm 2FA for a user.

    This endpoint is used to confirm the second factor authentication (2FA) for a user.
    It is typically called after the user has provided their TOTP code.

    Args:
        user: Request data containing the user's email, password, and TOTP code
        request: The HTTP request object to extract client information
        db: Database session dependency

    Returns:
        UserLoginResponse: Response containing user details upon successful confirmation

    Raises:
        HTTPException: If confirmation fails or user is not found
    """
    result = await db.execute(
        text(...),  # TODO
        {"p_app_id": totp.app_id, "p_token": totp.code},
    )
    data = result.scalar_one_or_none()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TOTP secret not found for user",
        )

    if not data.verify(totp.totp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code",
        )

    # Convert to response model for adding tokens
    user_dict = dict(data._mapping) if hasattr(data, "_mapping") else dict(data)

    # Create session and refresh tokens for the opaque token flow
    access_token, refresh_token = await create_login_session(totp.user_id, db, totp.app_id, totp.request)
    user_dict.update({"access_token": access_token, "refresh_token": refresh_token})
    return UserLoginResponse.model_validate(user_dict)
