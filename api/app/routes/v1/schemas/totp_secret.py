"""
Pydantic schemas for TOTP secret-related operations.

This module provides Pydantic schemas for validating TOTP secret-related data,
such as user requests and responses.
"""

from random import randint
from typing import Annotated

from pydantic import BaseModel, Field

from .application import AppFieldTypes
from .common import CommonFieldTypes
from .user import UserFieldTypes


class TOTPSecretFieldTypes:
    """Reusable field types for TOTP secret schemas."""

    Id = CommonFieldTypes.UUID
    CreatedAt = CommonFieldTypes.NonFutureTimestamp
    SecretEncrypted = CommonFieldTypes.EncryptedField
    SecretHash = CommonFieldTypes.HashedField
    UserId = UserFieldTypes.Id

    KeyVersion = Annotated[
        int,
        Field(
            title="Key Version",
            description="The version of the key used for encryption.",
            ge=1,
            le=10,  # Assuming a maximum of 10 versions for simplicity
            example=randint(1, 10),
            default=1,
        ),
    ]


class TOTPSecretChallengeRequest(BaseModel):
    """Schema for TOTP secret challenge request."""

    app_id: AppFieldTypes.Id
    token: CommonFieldTypes.Token
    code: Annotated[
        int,
        Field(
            description="The TOTP code provided by the user.",
            example=randint(100_000, 999_999),
            ge=100_000,
            le=999_999,
        ),
    ]
