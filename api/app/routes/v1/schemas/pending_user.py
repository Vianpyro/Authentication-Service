"""
Pydantic schemas for pending user-related operations.

This module provides Pydantic schemas for validating pending user-related data,
such as user requests and responses.
"""

from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from .application import AppFieldTypes
from .common import CommonFieldTypes
from .user import UserFieldTypes, validate_password_complexity


class PendingUserTypes:
    """Reusable field types for pending user schemas."""

    AppId = AppFieldTypes.Id

    CreatedAt = CommonFieldTypes.Timestamp

    ExpiresAt = CommonFieldTypes.Timestamp

    EmailEncrypted = CommonFieldTypes.EncryptedField

    EmailHash = CommonFieldTypes.HashedField

    Id = CommonFieldTypes.Id

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
            example="user@example.com",
        ),
    ]


class PendingUserConfirmation(BaseModel):
    """Schema for confirming a pending user registration."""

    app_id: PendingUserTypes.AppId

    token: PendingUserTypes.Token

    password: UserFieldTypes.Password

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        return validate_password_complexity(password)


class PendingUserConfirmationResponse(BaseModel):
    """Response schema for confirming a pending user registration."""

    user_id: UserFieldTypes.Id
