"""
Authentication utility functions for session and token management.

This module provides reusable functions for creating login sessions, MFA challenge sessions,
and other authentication-related operations used across multiple endpoints.
"""

from datetime import datetime

from app.utility.security.tokens import create_token, hash_token
from fastapi import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def create_login_session(
    user_id: int, db: AsyncSession, app_id: int, request: Request
) -> dict[str, str | datetime]:
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
        dict[str, str | datetime]: A dictionary containing session tokens and their expiration dates.
    """
    access_token = create_token()
    refresh_token = create_token()

    result = await db.execute(
        text(
            """
            SELECT access_token_expires_at, refresh_token_expires_at
            FROM create_session (
                p_app_id => :app_id,
                p_user_id => :user_id,
                p_access_token_hash => :access_token_hash,
                p_refresh_token_hash => :refresh_token_hash,
                p_ip_address => :ip_address,
                p_user_agent => :user_agent
            )"""
        ),
        {
            "app_id": app_id,
            "user_id": user_id,
            "access_token_hash": hash_token(access_token),
            "refresh_token_hash": hash_token(refresh_token),
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent", ""),
        },
    )
    data = result.fetchone()
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "access_token_expires_at": data.access_token_expires_at,
        "refresh_token_expires_at": data.refresh_token_expires_at,
    }


async def create_mfa_challenge_session(
    user_id: int, db: AsyncSession, app_id: int, request: Request
) -> str:
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
    await db.commit()

    return challenge_token
