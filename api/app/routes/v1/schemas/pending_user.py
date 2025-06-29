"""
Pydantic schemas for pending user-related operations.

This module provides Pydantic schemas for validating pending user-related data,
such as user requests and responses.
"""

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
