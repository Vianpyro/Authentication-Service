"""
Pending User Registration API Endpoints.

This module provides FastAPI endpoints for handling the two-step user registration process
in the authentication service. The registration flow consists of:

1. Initial registration (`POST /`) - Creates a pending user record and sends verification email
2. Confirmation (`POST /confirm`) - Validates the verification token and creates the user account

Features:
- Automatic cleanup of expired registrations
- Background email sending
- Comprehensive error handling with appropriate HTTP status codes

Security Features:
- Timing attack mitigation with minimum response times
- Secure email encryption and hashing
- Token-based email verification
- Email addresses are encrypted at rest and hashed for indexing
- Passwords are hashed using Argon2ID
- Verification tokens are cryptographically secure
- Rate limiting through minimum response times
- IP address and user agent tracking for audit purposes
"""

import asyncio
import time
from datetime import datetime
from random import uniform as jitter

from app.routes.v1.schemas.email import RegistrationEmailSchema
from app.routes.v1.schemas.pending_user import (
    PendingUserConfirmation,
    PendingUserConfirmationResponse,
    PendingUserCreate,
)
from app.utility.database import get_db
from app.utility.email.sender import send_email_background
from app.utility.security import (
    create_verification_token,
    encrypt_email,
    hash_email,
    hash_password,
)
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
MIN_RESPONSE_TIME_SECONDS = 0.45


@router.post(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Verification email sent successfully",
)
async def register_pending_user(
    background_tasks: BackgroundTasks,
    pending_user: PendingUserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Initiate user registration by creating a pending user record and sending verification email.

    This endpoint starts the two-step registration process by:
    1. Creating a pending user record with encrypted email and verification token
    2. Sending a verification email with a time-limited confirmation link
    3. Implementing timing attack mitigation with minimum response time

    The endpoint returns HTTP 204 No Content regardless of whether the email exists to prevent email enumeration attacks
    If the email is already registered, no verification email is sent.

    Args:
        background_tasks: FastAPI background tasks for async email sending
        pending_user: Registration data including email, app_id, and confirmation_url
        request: HTTP request object for extracting client metadata
        db: Database session dependency

    Returns:
        HTTP 204 No Content: Always returned to prevent email enumeration

    Security Features:
        - Minimum response time of ~0.5s to mitigate timing attacks
        - Email encryption at rest using application-level encryption
        - Email hashing for secure indexing without exposing plaintext
        - Cryptographically secure verification tokens
        - Client IP and user agent tracking for audit logs

    Raises:
        HTTPException: Only for unexpected database errors (integrity errors are silenced)
    """
    start = time.monotonic() + jitter(0, 0.1)

    try:
        result = await db.execute(
            text(
                """
                SELECT register_pending_user(
                    :p_app_id,
                    :p_token,
                    :p_email_encrypted,
                    :p_email_hash,
                    :p_ip_address,
                    :p_user_agent
                )
                """
            ),
            {
                "p_app_id": pending_user.app_id,
                "p_token": create_verification_token(),
                "p_email_encrypted": encrypt_email(pending_user.email),
                "p_email_hash": hash_email(pending_user.email),
                "p_ip_address": request.client.host if request.client else None,
                "p_user_agent": request.headers.get("user-agent", ""),
            },
        )
        expires_at = result.scalar()

    # Silently handle integrity errors (e.g., duplicate email)
    except IntegrityError:
        expires_at = None

    elapsed = time.monotonic() - start
    remaining_time = max(0, MIN_RESPONSE_TIME_SECONDS - elapsed)
    if remaining_time:
        await asyncio.sleep(remaining_time)

    if expires_at is None:
        return

    await db.commit()

    # Format expires_at to human readable string
    if isinstance(expires_at, datetime):
        if expires_at.tzinfo is not None:
            tz_name = expires_at.strftime("%Z") or expires_at.strftime("%z")
        else:
            tz_name = "UTC"

        expires_at_formatted = expires_at.strftime(f"%B %d, %Y at %I:%M %p {tz_name}")
    else:
        expires_at_formatted = str(expires_at)

    # Retrieve the application name from the database
    result = await db.execute(
        text("SELECT app_name FROM applications WHERE id = :app_id"),
        {"app_id": pending_user.app_id},
    )
    app_name = result.scalar()

    send_email_background(
        background_tasks,
        RegistrationEmailSchema(
            recipients=[pending_user.email],
            subject=f"{app_name} - Email Verification",
            body={
                "title": app_name,
                "confirmation_url": f"{pending_user.confirmation_url}?token={verification_token}",
                "expires_at": expires_at_formatted,
            },
            template_path="registration_email_v1.html",
        ),
    )


@router.post(
    "/confirm",
    status_code=status.HTTP_201_CREATED,
    response_model=PendingUserConfirmationResponse,
    response_description="User account created successfully",
)
async def confirm_pending_user(
    pending_user: PendingUserConfirmation,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Complete user registration by validating verification token and creating user account.

    This endpoint completes the two-step registration process by:
    1. Validating the verification token and checking expiration
    2. Creating the user account with the provided password
    3. Cleaning up the pending user record and token
    4. Returning the new user ID

    The endpoint performs comprehensive validation including token validity,
    expiration checks, and duplicate user detection.
    All validation errors are mapped to appropriate HTTP status codes.

    Args:
        pending_user: Confirmation data including app_id, token, and password
        request: HTTP request object for extracting client metadata
        db: Database session dependency

    Returns:
        PendingUserConfirmationResponse: Contains the newly created user ID

    Raises:
        HTTPException:
            - 404 Not Found: Invalid or expired verification token
            - 409 Conflict: User account already exists
            - 410 Gone: Token or registration has expired
            - 500 Internal Server Error: Unexpected database errors

    Security Features:
        - Verification token validation with cryptographic security
        - Password hashing using Argon2ID algorithm
        - Automatic cleanup of expired tokens and registrations
        - Client IP and user agent logging for audit trails
        - Atomic database operations to prevent race conditions
    """

    # Extract IP address and user agent from request
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")

    # Define error mappings for cleaner exception handling
    error_mappings = {
        "Pending user not found": (
            status.HTTP_404_NOT_FOUND,
            "Invalid or expired verification token",
        ),
        "Invalid verification token": (
            status.HTTP_404_NOT_FOUND,
            "Invalid verification token",
        ),
        "Token has expired": (
            status.HTTP_410_GONE,
            "Verification token has expired",
        ),
        "Registration has expired": (
            status.HTTP_410_GONE,
            "Registration has expired",
        ),
        "User already exists": (
            status.HTTP_409_CONFLICT,
            "User account already exists",
        ),
    }

    try:
        result = await db.execute(
            text(
                "SELECT confirm_pending_user(:p_app_id, :p_token, :p_password, :p_ip_address, :p_user_agent)"
            ),
            {
                "p_app_id": pending_user.app_id,
                "p_token": pending_user.token,
                "p_password": hash_password(pending_user.password),
                "p_ip_address": ip_address,
                "p_user_agent": user_agent,
            },
        )
        await db.commit()

        return PendingUserConfirmationResponse(user_id=result.scalar())

    except Exception as e:
        error_str = str(e)

        # Check for known database errors
        for error_msg, (status_code, detail) in error_mappings.items():
            if error_msg in error_str:
                raise HTTPException(status_code=status_code, detail=detail)

        # Re-raise unknown exceptions
        raise
