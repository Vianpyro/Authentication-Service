"""
Pydantic schemas for password reset token-related operations.

This module provides Pydantic schemas for validating password reset token-related data,
such as user requests and responses.
"""

from .common import CommonFieldTypes
from .user import UserFieldTypes


class PasswordResetTokenTypes:
    """Reusable field types for password reset token schemas."""

    CreatedAt = CommonFieldTypes.Timestamp

    ExpiresAt = CommonFieldTypes.Timestamp

    Id = CommonFieldTypes.Id

    Token = CommonFieldTypes.Token

    UserId = UserFieldTypes.Id
