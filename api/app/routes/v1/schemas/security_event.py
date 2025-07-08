"""
Pydantic schemas for security event-related operations.

This module provides Pydantic schemas for validating security event-related data,
such as user requests and responses.
"""

from typing import Annotated

from pydantic import Field

from .application import AppFieldTypes
from .common import CommonFieldTypes
from .user import UserFieldTypes


class SecurityEventTypes:
    """Reusable field types for security event schemas."""

    AppId = AppFieldTypes.Id
    Id = CommonFieldTypes.Id
    OccurredAt = CommonFieldTypes.NonFutureTimestamp
    UserId = UserFieldTypes.Id

    EventType = Annotated[
        str,
        Field(
            title="Event Type",
            pattern=r"^[a-z2_-]+$",
            description="The type of the security event",
            examples=[
                "password_changed",
                "2fa_enabled",
                "account_locked",
                "sanitized",
            ],
        ),
    ]

    Metadata = Annotated[
        dict,
        Field(
            description="Additional metadata about the security event",
            example={"ip_address": "192.168.1.1", "user_agent": "Mozilla/5.0"},
        ),
    ]
