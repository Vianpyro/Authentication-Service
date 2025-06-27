"""
Pydantic schemas for API request/response models.

This module defines the Pydantic models used for request and response validation.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

class UserBase(BaseModel):
    """Base schema for User."""

    email_encrypted: str
    email_hash: str
    phone_encrypted: Optional[str] = None
    phone_hash: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password_hash: str
    app_id: uuid.UUID


class UserResponse(UserBase):
    """Schema for user response."""

    id: uuid.UUID
    app_id: uuid.UUID
    is_email_verified: bool
    is_2fa_enabled: bool
    is_suspended: bool
    failed_login_count: int
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    scheduled_for_deletion_at: Optional[datetime] = None
    account_locked_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
