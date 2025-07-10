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

from dotenv import load_dotenv

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
