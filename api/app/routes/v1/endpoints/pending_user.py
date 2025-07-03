"""
User Registration endpoints for the API.

This module provides FastAPI endpoints for handling user registration in the authentication database.
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
    response_description="Pending user registration successful",
)
async def register_pending_user(
    background_tasks: BackgroundTasks,
    pending_user: PendingUserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user in the authentication database.

    Sets a minimum response time of ~0.5s to mitigate timing attacks.
    """
    start = time.monotonic() + jitter(0, 0.1)

    email_encrypted = encrypt_email(pending_user.email)
    email_hash = hash_email(pending_user.email)
    verification_token = create_verification_token()

    # Extract IP address and user agent from request
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")

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
                "p_token": verification_token,
                "p_email_encrypted": email_encrypted,
                "p_email_hash": email_hash,
                "p_ip_address": ip_address,
                "p_user_agent": user_agent,
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
)
async def confirm_pending_user(
    pending_user: PendingUserConfirmation,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Confirm a pending user registration and create the user account.

    This endpoint is used to confirm a pending user registration by providing the
    application ID, verification token, and optionally the user's IP address and user agent.
    It will create the user account in the database if the token is valid.
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
