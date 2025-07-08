"""
Pydantic schemas for pending user-related operations.

This module provides Pydantic schemas for validating pending user-related data,
such as user requests and responses.
"""

import random
import zoneinfo
from typing import Annotated

from pydantic import BaseModel, Field

from .application import AppFieldTypes
from .common import CommonFieldTypes
from .user import UserFieldTypes


class PendingUserTypes:
    """Reusable field types for pending user schemas."""

    AppId = AppFieldTypes.Id
    CreatedAt = CommonFieldTypes.NonFutureTimestamp
    ExpiresAt = CommonFieldTypes.FutureTimestamp
    EmailEncrypted = CommonFieldTypes.EncryptedField
    EmailHash = CommonFieldTypes.HashedField
    Id = CommonFieldTypes.Id
    Token = CommonFieldTypes.Token


class RegisterRequest(BaseModel):
    """Schema for creating a pending user."""

    app_id: AppFieldTypes.Id
    email: CommonFieldTypes.Email

    confirmation_url: Annotated[
        str,
        Field(
            title="Confirmation URL",
            description="The URL to confirm the pending user registration.",
        ),
    ]

    timezone: Annotated[
        str,
        Field(
            title="Timezone",
            pattern=r"^[a-zA-Z/_-]+$",
            description="The timezone of the user, used for formatting expiration times.",
            min_length=1,
            max_length=50,
            example=random.choice(sorted(zoneinfo.available_timezones())),
            default="UTC",
        ),
    ]


class RegisterConfirmationRequest(BaseModel):
    """Schema for confirming a pending user registration."""

    app_id: PendingUserTypes.AppId
    token: PendingUserTypes.Token
    password: UserFieldTypes.Password


class RegisterConfirmationResponse(BaseModel):
    """Response schema for confirming a pending user registration."""

    user_id: UserFieldTypes.Id
