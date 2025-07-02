"""
User Registration endpoints for the API.

This module provides FastAPI endpoints for handling user registration in the authentication database.
"""

import asyncio
import time
from datetime import datetime

from app.routes.v1.schemas.email import RegistrationEmailSchema
from app.routes.v1.schemas.pending_user import PendingUserCreate
from app.utility.database import get_db
from app.utility.email.sender import send_email_background
from app.utility.security import create_verification_token, encrypt_email, hash_email
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
MIN_RESPONSE_TIME_SECONDS = 0.5


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
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
    start = time.monotonic()

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
        expires_at_formatted = expires_at.strftime("%B %d, %Y at %I:%M %p UTC")
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
