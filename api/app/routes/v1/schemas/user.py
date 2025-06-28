"""
Pydantic schemas for user-related operations.

This module provides Pydantic schemas for validating user-related data,
such as user requests and responses.
"""

from typing import Annotated

from pydantic import Field

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

    UpdatedAt = CommonFieldTypes.UpdatedAt
