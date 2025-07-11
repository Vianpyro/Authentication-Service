"""
Security module for hashing, encryption, and token verification.

This module provides functions and constants for handling password hashing,
field encryption/decryption, OTP verification, and normalization of sensitive
fields such as email and phone numbers. It is used throughout the application
to ensure secure handling of user credentials and sensitive data.
"""

import hashlib
import hmac
import os
import secrets

from app.utility.database import get_db
from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

TOKEN_PEPPER = os.getenv("TOKEN_PEPPER", "").encode("utf-8")
FIELD_HASH_SALT = os.getenv("FIELD_HASH_SALT", "public-tenant-aware-salt").encode("utf-8")

if not TOKEN_PEPPER:
    raise RuntimeError("Missing required secret: TOKEN_PEPPER")


def create_token(num_bytes: int = 32) -> str:
    """Generate a secure URL-safe token."""
    return secrets.token_urlsafe(num_bytes)


def hash_token(token: str) -> bytes:
    """Hash a token using HMAC with SHA-256 and a pepper."""
    return hmac.new(TOKEN_PEPPER, token.encode("utf-8"), hashlib.sha256).digest()


def verify_token(token: str, stored_hash: bytes) -> bool:
    """Constant-time check of a token."""
    return hmac.compare_digest(hash_token(token), stored_hash)


async def require_access_token(
    authorization: str = Header(..., alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    token = authorization.removeprefix("Bearer ").strip()
    token_hash = hash_token(token)

    result = await db.execute(
        text("SELECT * FROM get_access_token(p_token_hash => :p_token_hash)"),
        {"p_token_hash": token_hash},
    )

    session = result.fetchone()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    return session


async def require_challenge_token(
    mfa_challenge: str = Header(..., alias="X-TOTP-Challenge"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if not mfa_challenge.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid challenge header format",
        )
    token = mfa_challenge.removeprefix("Bearer ").strip()

    result = await db.execute(
        text("SELECT * FROM get_totp_secret(p_token_hash => :p_token_hash)"),
        {"p_token_hash": hash_token(token)},
    )
    data = result.fetchone()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="TOTP challenge token invalid or expired",
        )
    return data
