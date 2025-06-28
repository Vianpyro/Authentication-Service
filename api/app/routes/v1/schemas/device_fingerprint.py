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

    FingerprintHash = CommonFieldTypes.HashedField

    Id = CommonFieldTypes.UUID

    DeviceName = Annotated[
        str,
        Field(
            title="Device Name",
            min_length=1,
            max_length=100,
            description="The name of the device",
            examples=["iPhone 12", "Samsung Galaxy S21"],
        ),
    ]

    UserAgent = CommonFieldTypes.UserAgent

    LastSeenAt = CommonFieldTypes.Timestamp

    UserId = UserFieldTypes.Id
