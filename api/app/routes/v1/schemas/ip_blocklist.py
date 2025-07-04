"""
Pydantic schemas for IP blocklist-related operations.

This module provides Pydantic schemas for validating IP blocklist-related data.
"""

from datetime import timedelta
from typing import Annotated

from pydantic import Field

from .common import CommonFieldTypes
from .user import UserFieldTypes


class IPBlocklistTypes:
    """Reusable field types for IP blocklist schemas."""

    BlockedAt = CommonFieldTypes.NonFutureTimestamp

    BlockedByUser = UserFieldTypes.Id

    Duration = Annotated[
        timedelta,
        Field(
            title="Duration",
            description="The duration of the block",
            default=timedelta(days=3),
            examples=[
                timedelta(minutes=15),
                timedelta(days=3),
                timedelta(days=28),
                timedelta(years=10),
            ],
        ),
    ]

    IpAddress = CommonFieldTypes.IpAddress

    ManualBlock = Annotated[
        bool,
        Field(
            title="Manual Block",
            description="Indicates whether the block was manually created",
            examples=[True, False],
            default=False,
        ),
    ]

    Reason = Annotated[
        str,
        Field(
            title="Reason",
            description="The reason for the IP block",
            examples=[
                "abusive behavior",
                "spamming",
                "brute force attack",
            ],
        ),
    ]
