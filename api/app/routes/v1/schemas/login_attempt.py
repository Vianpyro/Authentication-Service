"""
Pydantic schemas for login attempt-related operations.

This module provides Pydantic schemas for validating login attempt-related data,
such as user requests and responses.
"""

from typing import Annotated

from pydantic import Field

from .application import AppFieldTypes
from .common import CommonFieldTypes
from .user import UserFieldTypes


class LoginAttemptTypes:
    """Reusable field types for login attempt schemas."""

    AppId = AppFieldTypes.Id

    AttemptedAt = CommonFieldTypes.NonFutureTimestamp

    EmailEncrypted = CommonFieldTypes.EncryptedField

    EmailHashed = CommonFieldTypes.HashedField

    Id = CommonFieldTypes.Id

    IpAddress = CommonFieldTypes.IpAddress

    UserAgent = CommonFieldTypes.UserAgent

    UserId = UserFieldTypes.Id

    WasSuccessful = Annotated[
        bool,
        Field(
            description="Indicates whether the login attempt was successful.",
            examples=[True, False],
        ),
    ]
