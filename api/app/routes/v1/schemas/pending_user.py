"""
Pydantic schemas for pending user-related operations.

This module provides Pydantic schemas for validating pending user-related data,
such as user requests and responses.
"""

from typing import Annotated

from pydantic import BaseModel, Field

from .application import AppFieldTypes
from .common import CommonFieldTypes


class PendingUserTypes:
    """Reusable field types for pending user schemas."""

    AppId = AppFieldTypes.Id

    CreatedAt = CommonFieldTypes.Timestamp

    ExpiresAt = CommonFieldTypes.Timestamp

    EmailEncrypted = CommonFieldTypes.EncryptedField

    EmailHash = CommonFieldTypes.HashedField

    Id = CommonFieldTypes.Id

    IpAddress = CommonFieldTypes.IpAddress

    UserAgent = CommonFieldTypes.UserAgent

    Token = CommonFieldTypes.Token


class PendingUserCreate(BaseModel):
    """Schema for creating a pending user."""

    app_id: AppFieldTypes.Id

    confirmation_url: Annotated[
        str,
        Field(
            title="Confirmation URL",
            description="The URL to confirm the pending user registration.",
        ),
    ]

    email: Annotated[
        str,
        Field(
            title="Email",
            description="The email address of the pending user.",
            examples=["user@example.com"],
        ),
    ]
