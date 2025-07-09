"""
Security module for hashing, encryption, and token verification.

This module provides functions and constants for handling password hashing,
field encryption/decryption, OTP verification, and normalization of sensitive
fields such as email and phone numbers. It is used throughout the application
to ensure secure handling of user credentials and sensitive data.
"""

import base64
import hashlib
import hmac
import os
import secrets
import unicodedata
from re import search

import pyotp
from argon2 import PasswordHasher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

load_dotenv()

# --- Constants ---
ph = PasswordHasher()
AES_KEY = bytes.fromhex(os.getenv("AES_SECRET_KEY") or "")
PASSWORD_PEPPER = os.getenv("PASSWORD_PEPPER", "")
TOKEN_PEPPER = os.getenv("TOKEN_PEPPER", "").encode("utf-8")
FIELD_HASH_SALT = os.getenv("FIELD_HASH_SALT", "public-tenant-aware-salt").encode(
    "utf-8"
)

if not AES_KEY or not PASSWORD_PEPPER or not TOKEN_PEPPER:
    raise RuntimeError(
        "Missing required secrets: AES_SECRET_KEY, PASSWORD_PEPPER, or TOKEN_PEPPER"
    )


# --- Token Utilities ---
def create_token(num_bytes: int = 32) -> str:
    """Generate a secure URL-safe token."""
    return secrets.token_urlsafe(num_bytes)


def hash_token(token: str) -> bytes:
    """Hash a token using HMAC with SHA-256 and a pepper."""
    return hmac.new(TOKEN_PEPPER, token.encode("utf-8"), hashlib.sha256).digest()


def verify_token(token: str, stored_hash: bytes) -> bool:
    """Constant-time check of a token."""
    return hmac.compare_digest(hash_token(token), stored_hash)


# --- Password Utilities ---
def hash_password(password: str) -> str:
    """Hash a password using Argon2 and a pepper."""
    peppered = unicodedata.normalize("NFKC", password) + PASSWORD_PEPPER
    return ph.hash(peppered)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password using Argon2 and pepper."""
    peppered = unicodedata.normalize("NFKC", password) + PASSWORD_PEPPER
    try:
        return ph.verify(hashed_password, peppered)
    except Exception:
        return False


def validate_password_complexity(password: str) -> str:
    """
    Validates a password based on the following criteria:
    - At least 12 characters long.
    - Contains at least one uppercase letter (A-Z).
    - Contains at least one lowercase letter (a-z).
    - Contains at least one digit (0-9).
    - Contains at least one special character (any non-alphanumeric character).
    """
    error_messages = []

    if len(password) < 12:
        error_messages.append("must be at least 12 characters long")

    if not search(r"[A-Z]", password):
        error_messages.append("must contain at least one uppercase letter")

    if not search(r"[a-z]", password):
        error_messages.append("must contain at least one lowercase letter")

    if not search(r"\d", password):
        error_messages.append("must contain at least one digit")

    if not search(r"[^A-Za-z0-9]", password):
        error_messages.append("must contain at least one special character")

    if error_messages:
        combined_message = f"Password validation failed: {'; '.join(error_messages)}"
        raise ValueError(combined_message)

    return password


# --- AES Encryption ---
def encrypt_field(value: str) -> str:
    """Encrypt a string using AES-256-GCM (returns base64 string)."""
    aesgcm = AESGCM(AES_KEY)
    iv = os.urandom(12)
    ciphertext = aesgcm.encrypt(iv, value.encode("utf-8"), associated_data=None)
    return base64.b64encode(iv + ciphertext).decode("utf-8")


def decrypt_field(encrypted_base64: str) -> str:
    """Decrypt a base64-encoded AES-256-GCM encrypted value."""
    data = base64.b64decode(encrypted_base64)
    iv, ciphertext = data[:12], data[12:]
    return AESGCM(AES_KEY).decrypt(iv, ciphertext, associated_data=None).decode("utf-8")


# --- Field Hashing ---
def hash_field(value: str, namespace: str) -> str:
    """SHA-256 hash of a UTF-8 value, for indexing."""
    return hashlib.sha256(f"{namespace}:{value}".encode("utf-8")).hexdigest()


def hash_email(email: str, namespace: str) -> str:
    """
    Generate a SHA-256 hash of the normalized email (used for fast lookup).
    Normalizes by removing subdomain aliases (part after + and before @) to prevent duplicates.

    Args:
        email (str): The email address.

    Returns:
        str: The SHA-256 hash of the normalized email.
    """
    normalized_email = email.lower()

    if "+" in normalized_email:
        local_part, domain_part = normalized_email.rsplit("@", 1)
        local_part = local_part.split("+")[0]
        normalized_email = f"{local_part}@{domain_part}"

    return hash_field(normalized_email, namespace)


# --- OTP Verification ---
def verify_otp(
    secret: str, otp_code: str, method: str = "TOTP", counter: int = 0
) -> bool:
    """Verify a one-time password (TOTP or HOTP)."""
    try:
        if method == "TOTP":
            return pyotp.TOTP(secret).verify(otp_code)
        elif method == "HOTP":
            return pyotp.HOTP(secret).verify(otp_code, counter)
        return False
    except Exception:
        return False
