"""
Pydantic schemas for user-related operations.

This module provides Pydantic schemas for validating user-related data,
such as user requests and responses.
"""

from random import choice
from string import ascii_letters
from typing import Annotated

from app.utils.security.password import hash_password, validate_password_complexity
from pydantic import AfterValidator, BaseModel, Field

from .application import AppFieldTypes
from .common import CommonFieldTypes


class UserFieldTypes:
    """Reusable field types for user schemas."""

    AccountLockedAt = CommonFieldTypes.NonFutureTimestamp
    AppId = AppFieldTypes.Id
    CreatedAt = CommonFieldTypes.NonFutureTimestamp
    EmailEncrypted = CommonFieldTypes.EncryptedField
    EmailHash = CommonFieldTypes.HashedField
    Id = CommonFieldTypes.UUID
    LastLoginAt = CommonFieldTypes.NonFutureTimestamp
    PhoneEncrypted = CommonFieldTypes.EncryptedField
    PhoneHash = CommonFieldTypes.HashedField
    ScheduledForDeletionAt = CommonFieldTypes.NonFutureTimestamp
    UpdatedAt = CommonFieldTypes.NonFutureTimestamp

    FailedLoginCount = Annotated[
        int,
        Field(
            title="Failed Login Count",
            description="Number of failed login attempts",
            ge=0,
            le=10,  # Assuming a reasonable upper limit for failed attempts
            examples=[0, 1, 2, 3, 5, 10],
        ),
    ]

    Is2FAEnabled = Annotated[
        bool,
        Field(
            title="Is 2FA Enabled",
            description="Indicates whether the user has 2FA enabled",
            examples=[True, False],
        ),
    ]

    IsEmailVerified = Annotated[
        bool,
        Field(
            title="Is Email Verified",
            description="Indicates whether the user's email address is verified",
            examples=[True, False],
        ),
    ]

    IsSuspended = Annotated[
        bool,
        Field(
            title="Is Suspended",
            description="Indicates whether the user is suspended",
            examples=[True, False],
        ),
    ]

    Password = Annotated[
        str,
        Field(
            title="Password",
            description="User's password with minimum 12 characters, letters, numbers, and symbols",
            min_length=12,
            example="StrongPassword123!",
        ),
        AfterValidator(validate_password_complexity),
    ]

    PasswordHash = Annotated[
        str,
        Field(
            title="Password Hash",
            pattern=r"^\$argon2id\$v=\d+\$m=\d+,t=\d+,p=\d+\$[a-zA-Z0-9+\/=]+\$[a-zA-Z0-9+\/=]+$",
            description="Hash of the user's password",
            examples=[
                "$argon2id$v=19$m=65536,t=3,p=4$[salt]$[hash]",
                hash_password("".join(choice(ascii_letters) for _ in range(10))),
            ],
        ),
    ]


class UserLoginRequest(BaseModel):
    """
    Schema for user login.

    This schema is used to validate the data required for user registration.
    It includes fields for email, password, and optional metadata.
    """

    app_id: UserFieldTypes.AppId
    email: CommonFieldTypes.Email
    password: UserFieldTypes.Password


class UserLoginResponse(BaseModel):
    """
    Response schema for user login.

    This schema is used to return the user ID after successful login.
    """

    id: UserFieldTypes.Id
    is_email_verified: UserFieldTypes.IsEmailVerified
    is_2fa_enabled: UserFieldTypes.Is2FAEnabled

    class Config:
        from_attributes = True


class UserLogin2faResponse(BaseModel):
    """
    Response schema for user login.

    This schema is used to return the user ID after successful login.
    """

    id: UserFieldTypes.Id
    is_email_verified: UserFieldTypes.IsEmailVerified
    is_2fa_enabled: UserFieldTypes.Is2FAEnabled

    class Config:
        from_attributes = True
