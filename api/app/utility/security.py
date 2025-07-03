"""
Security utility module for encryption, hashing, and authentication.

This module provides functions and constants for handling password hashing,
field encryption/decryption, OTP verification, and normalization of sensitive
fields such as email and phone numbers. It is used throughout the application
to ensure secure handling of user credentials and sensitive data.
"""

import base64
import hashlib
import os
import secrets
import unicodedata
from re import match

import pyotp
from argon2 import PasswordHasher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ph = PasswordHasher()

AES_KEY = bytes.fromhex(os.getenv("AES_SECRET_KEY", os.urandom(32).hex()))
PEPPER = os.getenv("PEPPER", "SuperSecretPepper")


def create_token(length: int) -> str:
    """
    Generate a secure random token for session management.
    Returns:
        str: A URL-safe, random token string.
    """
    return secrets.token_urlsafe(length)


def create_verification_token() -> str:
    """
    Generate a secure random token for email verification.

    Returns:
        str: A URL-safe, random token string.
    """
    return create_token(32)


def create_access_token() -> str:
    """
    Generate a secure random token for access control.

    Returns:
        str: A URL-safe, random token string.
    """
    return create_token(32)


def create_refresh_token() -> str:
    """
    Generate a secure random token for refresh operations.

    Returns:
        str: A URL-safe, random token string.
    """
    return create_token(64)


def encrypt_field(value: str) -> str:
    """
    Encrypt a value using AES-256-GCM.

    Args:
        value (str): The value to encrypt.

    Returns:
        str: Base64-encoded string of IV + ciphertext + tag.
    """
    aesgcm = AESGCM(AES_KEY)
    iv = os.urandom(12)  # 96-bit IV recommended for AES-GCM
    ciphertext = aesgcm.encrypt(iv, value.encode("utf-8"), associated_data=None)
    return base64.b64encode(iv + ciphertext).decode("utf-8")


def decrypt_field(encrypted_base64: str) -> str:
    """
    Decrypt a value encrypted with AES-256-GCM.

    Args:
        encrypted_base64 (str): The base64-encoded encrypted value.

    Returns:
        str: The decrypted string.
    """
    encrypted_data = base64.b64decode(encrypted_base64)
    iv, ciphertext = encrypted_data[:12], encrypted_data[12:]
    aesgcm = AESGCM(AES_KEY)
    decrypted = aesgcm.decrypt(iv, ciphertext, associated_data=None)
    return decrypted.decode("utf-8")


def hash_field(value: str) -> str:
    """
    Generate a SHA-256 hash of a field (used for fast lookup).

    Args:
        value (str): The value to hash.

    Returns:
        str: The SHA-256 hash as a hexadecimal string.
    """
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2 and a pepper.

    Args:
        password (str): The plaintext password.

    Returns:
        str: The Argon2 hash of the peppered password.
    """
    normalized = unicodedata.normalize("NFKC", password)
    peppered = normalized + PEPPER
    return ph.hash(peppered)


def verify_otp(
    secret: str, otp_code: str, otp_method: str = "TOTP", counter: int = 0
) -> bool:
    """
    Verify a one-time password (OTP) against a secret using TOTP or HOTP.

    Args:
        secret (str): The OTP secret.
        otp_code (str): The OTP code to verify.
        otp_method (str): The OTP method ("TOTP" or "HOTP").
        counter (int): The HOTP counter (required for HOTP).

    Returns:
        bool: True if the OTP is valid, False otherwise.
    """
    try:
        match otp_method:
            case "TOTP":
                return pyotp.TOTP(secret).verify(otp_code)
            case "HOTP":
                return pyotp.HOTP(secret).verify(otp_code, counter)
            case _:
                raise ValueError("Unsupported OTP method")
    except Exception:
        return False


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hashed password.

    Args:
        hashed_password (str): The Argon2 hashed password.
        password (str): The plaintext password to verify.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    peppered = unicodedata.normalize("NFKC", password) + PEPPER
    try:
        return ph.verify(hashed_password, peppered)
    except Exception:
        return False


def hash_email(email: str) -> str:
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

    return hash_field(normalized_email)


def hash_phone(phone: str) -> str:
    """
    Generate a SHA-256 hash of the phone number (used for fast lookup).

    Args:
        phone (str): The phone number.

    Returns:
        str: The SHA-256 hash of the phone number.
    """
    return hash_field(phone)


def hash_token(token: str) -> str:
    """
    Generate a SHA-256 hash of the token (used for fast lookup).

    Args:
        token (str): The token to hash.

    Returns:
        str: The SHA-256 hash of the token.
    """
    return hash_field(token)


def encrypt_email(email: str) -> str:
    """
    Encrypt the email address.

    Args:
        email (str): The email address to encrypt.

    Returns:
        str: The encrypted email.
    """
    return encrypt_field(email)


def encrypt_phone(phone: str) -> str:
    """
    Encrypt the normalized phone number.

    Args:
        phone (str): The phone number to encrypt.

    Returns:
        str: The encrypted phone number.
    """
    return encrypt_field(phone)
