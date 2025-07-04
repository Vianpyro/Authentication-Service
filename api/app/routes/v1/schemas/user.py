"""
Pydantic schemas for user-related operations.

This module provides Pydantic schemas for validating user-related data,
such as user requests and responses.
"""

from random import choice
from re import search
from string import ascii_letters
from typing import Annotated

from app.utility.security import hash_password
from pydantic import AfterValidator, Field

from .application import AppFieldTypes
from .common import CommonFieldTypes


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


class UserFieldTypes:
    """Reusable field types for user schemas."""

    AccountLockedAt = CommonFieldTypes.NonFutureTimestamp

    AppId = AppFieldTypes.Id

    CreatedAt = CommonFieldTypes.NonFutureTimestamp

    EmailEncrypted = CommonFieldTypes.EncryptedField

    EmailHash = CommonFieldTypes.HashedField

    FailedLoginCount = Annotated[
        int,
        Field(
            title="Failed Login Count",
            description="Number of failed login attempts",
            examples=[0, 1, 2],
        ),
    ]

    Id = CommonFieldTypes.UUID

    Is2FAEnabled = Annotated[
        bool,
        Field(
            title="Is 2FA Enabled",
            description="Indicates whether the user has 2FA enabled",
            examples=[True, False],
        ),
    ]

    IsEmailVerified = Annotated[
        bool,
        Field(
            title="Is Email Verified",
            description="Indicates whether the user's email address is verified",
            examples=[True, False],
        ),
    ]

    IsSuspended = Annotated[
        bool,
        Field(
            title="Is Suspended",
            description="Indicates whether the user is suspended",
            examples=[True, False],
        ),
    ]

    LastLoginAt = CommonFieldTypes.NonFutureTimestamp

    Password = Annotated[
        str,
        Field(
            title="Password",
            description="User's password, must be at least 12 characters long and contain a mix of letters, numbers, and symbols",
            min_length=12,
            example="StrongPassword123!",
        ),
        AfterValidator(validate_password_complexity),
    ]

    PasswordHash = Annotated[
        str,
        Field(
            title="Password Hash",
            pattern=r"^\$argon2id\$v=\d+\$m=\d+,t=\d+,p=\d+\$[a-zA-Z0-9+\/=]+\$[a-zA-Z0-9+\/=]+$",
            description="Hash of the user's password",
            examples=[
                "$argon2id$v=19$m=65536,t=3,p=4$[salt]$[hash]",
                hash_password("".join(choice(ascii_letters) for _ in range(10))),
            ],
        ),
    ]

    PhoneEncrypted = CommonFieldTypes.EncryptedField

    PhoneHash = CommonFieldTypes.HashedField

    ScheduledForDeletionAt = CommonFieldTypes.NonFutureTimestamp

    UpdatedAt = CommonFieldTypes.NonFutureTimestamp
