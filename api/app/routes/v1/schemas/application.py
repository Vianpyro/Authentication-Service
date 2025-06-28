"""
Pydantic schemas for API request/response models.

This module defines the Pydantic models used for request and response validation.
"""

import uuid
from typing import Annotated

from pydantic import BaseModel, Field


class AppFieldTypes:
    """Reusable field types for application schemas."""

    AppName = Annotated[
        str,
        Field(
            min_length=3,
            max_length=100,
            description="Human-readable application name",
            examples=["My Application", "User Service", "API Gateway"],
        ),
    ]

    Slug = Annotated[
        str,
        Field(
            pattern=r"^[a-z0-9][a-z0-9_-]{1,48}[a-z0-9]$",
            min_length=3,
            max_length=50,
            description="Application slug: 3-50 characters, lowercase letters, numbers, hyphens, and underscores. Must start and end with alphanumeric characters.",
            examples=["my-app", "user-service", "api_gateway", "service123"],
        ),
    ]

    Id = Annotated[
        uuid.UUID,
        Field(
            description="Unique identifier for the application",
            examples=["123e4567-e89b-12d3-a456-426614174000"],
        ),
    ]


class AppCreate(BaseModel):
    """Schema for creating a new application."""

    slug: AppFieldTypes.Slug
    app_name: AppFieldTypes.AppName


class AppCreateResponse(BaseModel):
    """Schema for application response."""

    id: uuid.UUID = AppFieldTypes.Id


class AppDeleteResponse(BaseModel):
    """Schema for application deletion response."""

    slug: AppFieldTypes.Slug
