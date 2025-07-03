"""
Pydantic schemas for user-related operations.

This module provides Pydantic schemas for validating user-related data,
such as user requests and responses.
"""

import re
from typing import Annotated

from pydantic import Field, field_validator

from .application import AppFieldTypes
from .common import CommonFieldTypes


class UserFieldTypes:
    """Reusable field types for user schemas."""

    AccountLockedAt = CommonFieldTypes.Timestamp

    AppId = AppFieldTypes.Id

    CreatedAt = CommonFieldTypes.Timestamp

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

    LastLoginAt = CommonFieldTypes.Timestamp

    Password = Annotated[
        str,
        Field(
            title="Password",
            description="User's password, must be at least 12 characters long and contain a mix of letters, numbers, and symbols",
            min_length=12,
            examples=["StrongPassword123!"],
        ),
    ]

    PasswordHash = Annotated[
        str,
        Field(
            title="Password Hash",
            pattern=r"^\$argon2id\$v=\d+\$m=\d+,t=\d+,p=\d+\$[a-zA-Z0-9+\/=]+\$[a-zA-Z0-9+\/=]+$",
            description="Hash of the user's password",
            examples=["$argon2id$v=19$m=65536,t=3,p=4$[salt]$[hash]"],
        ),
    ]

    PhoneEncrypted = CommonFieldTypes.EncryptedField

    PhoneHash = CommonFieldTypes.HashedField

    ScheduledForDeletionAt = CommonFieldTypes.Timestamp

    UpdatedAt = CommonFieldTypes.Timestamp

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """Validate password complexity requirements."""
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters long")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("Password must contain at least one special character")

        return v
