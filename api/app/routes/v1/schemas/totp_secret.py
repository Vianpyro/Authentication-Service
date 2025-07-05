"""
Pydantic schemas for TOTP secret-related operations.

This module provides Pydantic schemas for validating TOTP secret-related data,
such as user requests and responses.
"""

from typing import Annotated

from pydantic import Field

from .common import CommonFieldTypes
from .user import UserFieldTypes


class TOTPSecretTypes:
    """Reusable field types for TOTP secret schemas."""

    Id = CommonFieldTypes.UUID

    CreatedAt = CommonFieldTypes.NonFutureTimestamp

    KeyVersion = Annotated[
        int,
        Field(
            description="The version of the key used for encryption.",
            example=1,
            default=1,
        ),
    ]

    SecretEncrypted = CommonFieldTypes.EncryptedField

    SecretHash = CommonFieldTypes.HashedField

    UserId = UserFieldTypes.Id
