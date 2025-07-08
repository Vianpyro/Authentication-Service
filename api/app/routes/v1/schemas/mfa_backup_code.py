"""
Pydantic schemas for MFA backup code-related operations.

This module provides Pydantic schemas for validating MFA backup code-related data,
such as user requests and responses.
"""

from typing import Annotated

from pydantic import Field

from .application import AppFieldTypes
from .common import CommonFieldTypes
from .user import UserFieldTypes


class MFABackupCodeTypes:
    """Reusable field types for MFA backup code schemas."""

    AppId = AppFieldTypes.Id
    CodeHash = CommonFieldTypes.HashedField
    CreatedAt = CommonFieldTypes.NonFutureTimestamp
    Id = CommonFieldTypes.UUID
    UserId = UserFieldTypes.Id

    Used = Annotated[
        bool,
        Field(
            description="Indicates whether the backup code has been used.",
            examples=[True, False],
            default=False,
        ),
    ]
