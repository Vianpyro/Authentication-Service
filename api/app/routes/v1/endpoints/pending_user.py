"""
User Registration endpoints for the API.

This module provides FastAPI endpoints for handling user registration in the authentication database.
"""

from app.routes.v1.schemas.pending_user import (
    PendingUserCreate,
    PendingUserCreateResponse,
)
from app.utility.database import get_db
from app.utility.security import create_verification_token, encrypt_email, hash_email
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def register_pending_user(
    pending_user: PendingUserCreate, db: AsyncSession = Depends(get_db)
):
    "Register a new user in the authentication database."
    email_encrypted = encrypt_email(pending_user.email)
    email_hash = hash_email(pending_user.email)
    verification_token = create_verification_token()

    result = await db.execute(
        text(
            "CALL register_pending_user(:p_app_id, :p_email_encrypted, :p_email_hash, :p_token)"
        ),
        {
            "p_app_id": pending_user.app_id,
            "p_email_encrypted": email_encrypted,
            "p_email_hash": email_hash,
            "p_token": verification_token,
        },
    )
    pending_user_id = result.scalar_one_or_none()

    if pending_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to register pending user",
        )

    await db.commit()
    return PendingUserCreateResponse()
