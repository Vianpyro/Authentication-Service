"""
Pydantic schemas for API request/response models.

This module defines the Pydantic models used for request and response validation.
"""

import uuid

from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    """Schema for creating a new application."""

    slug: str
    app_name: str


class ApplicationResponse(BaseModel):
    """Schema for application response."""

    id: uuid.UUID
