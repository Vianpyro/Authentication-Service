"""
Pydantic schemas for device fingerprint-related operations.

This module provides Pydantic schemas for validating device fingerprint-related data,
such as user requests and responses.
"""

from typing import Annotated

from pydantic import Field

from .application import AppFieldTypes
from .common import CommonFieldTypes
from .user import UserFieldTypes


class DeviceFingerprintTypes:
    """Reusable field types for device fingerprint schemas."""

    AppId = AppFieldTypes.Id

    CreatedAt = CommonFieldTypes.Timestamp

    ExpiresAt = CommonFieldTypes.Timestamp

    Id = CommonFieldTypes.Id

    IpAddress = CommonFieldTypes.IpAddress

    IsActive = Annotated[
        bool,
        Field(
            title="Is Active",
            description="Indicates whether the session is active",
            examples=[True, False],
            default=True,
        ),
    ]

    Token = CommonFieldTypes.Token

    TokenType = Annotated[
        str,
        Field(
            title="Token Type",
            pattern=r"^[a-z]+$",
            description="The type of the token",
            examples=["access", "refresh"],
        ),
    ]

    UserAgent = CommonFieldTypes.UserAgent

    UserId = UserFieldTypes.Id
