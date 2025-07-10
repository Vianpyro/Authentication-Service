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
import zoneinfo
from datetime import datetime, timezone
from random import uniform as jitter

from app.utility.database import get_db
from app.utility.email.sender import send_email_background
from app.utility.security import create_token
from app.utility.security import encrypt_field as encrypt_email
from app.utility.security import hash_email, hash_token
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.email import RegistrationEmailSchema
from ...schemas.pending_user import RegisterRequest

router = APIRouter()
MIN_RESPONSE_TIME_SECONDS = 0.45


@router.post("", status_code=status.HTTP_204_NO_CONTENT, response_description="Verification email sent successfully")
async def register_pending_user(
    background_tasks: BackgroundTasks,
    request_body: RegisterRequest,
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
    verification_token = create_token()

    try:
        result = await db.execute(
            text(
                """
                SELECT register_pending_user(
                    p_app_id => :app_id,
                    p_token_hash => :token_hash,
                    p_email_encrypted => :email_encrypted,
                    p_email_hash => :email_hash,
                    p_ip_address => :ip_address,
                    p_user_agent => :user_agent
                )
                """
            ),
            {
                "app_id": request_body.app_id,
                "token_hash": hash_token(verification_token),
                "email_encrypted": encrypt_email(request_body.email),
                "email_hash": hash_email(request_body.email, request_body.app_id),
                "ip_address": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent", ""),
            },
        )
        expires_at = result.scalar_one_or_none()

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
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if request_body.timezone:
            try:
                user_tz = zoneinfo.ZoneInfo(request_body.timezone)
                expires_at_local = expires_at.astimezone(user_tz)
                tz_name = expires_at_local.strftime("%Z")
                expires_at_formatted = expires_at_local.strftime(f"%B %d, %Y at %I:%M %p {tz_name}")
            except (zoneinfo.ZoneInfoNotFoundError, ValueError):
                expires_at_formatted = expires_at.strftime("%B %d, %Y at %I:%M %p UTC")
        else:
            expires_at_formatted = expires_at.strftime("%B %d, %Y at %I:%M %p UTC")
    else:
        expires_at_formatted = str(expires_at)

    # Retrieve the application name from the database
    result = await db.execute(text("SELECT get_application_name(:app_id)"), {"app_id": request_body.app_id})
    app_name = result.scalar_one_or_none()

    send_email_background(
        background_tasks,
        RegistrationEmailSchema(
            recipients=[request_body.email],
            subject=f"{app_name} - Email Verification",
            body={
                "title": app_name,
                "confirmation_url": f"{request_body.confirmation_url}?token={verification_token}",
                "expires_at": expires_at_formatted,
            },
            template_path="registration_email_v1.html",
        ),
    )
