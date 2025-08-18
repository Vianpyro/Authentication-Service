import os
import unicodedata
from re import search

from argon2 import PasswordHasher
from dotenv import load_dotenv

load_dotenv()
ph = PasswordHasher()

PASSWORD_PEPPER = os.getenv("PASSWORD_PEPPER", "")

if not PASSWORD_PEPPER:
    raise RuntimeError("Missing required secret: PASSWORD_PEPPER")


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
    errors = []

    if len(password) < 12:
        errors.append("must be at least 12 characters long")

    if len(password) > 200:
        errors.append("must not exceed 200 characters")  # Potential buffer overflow attempt

    if not search(r"[A-Z]", password):
        errors.append("must contain at least one uppercase letter")

    if not search(r"[a-z]", password):
        errors.append("must contain at least one lowercase letter")

    if not search(r"\d", password):
        errors.append("must contain at least one digit")

    if not search(r"[^A-Za-z0-9]", password):
        errors.append("must contain at least one special character")

    if errors:
        combined_message = f"Password validation failed: {'; '.join(errors)}"
        raise ValueError(combined_message)

    return password
