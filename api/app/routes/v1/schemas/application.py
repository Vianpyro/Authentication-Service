"""
Pydantic schemas for API request/response models.

This module defines the Pydantic models used for request and response validation.
"""

from typing import Annotated

from pydantic import BaseModel, Field

from .common import CommonFieldTypes


class AppFieldTypes:
    """Reusable field types for application schemas."""

    AppName = Annotated[
        str,
        Field(
            title="Application Name",
            min_length=3,
            max_length=100,
            description="Human-readable application name",
            examples=["My Application", "User Service", "API Gateway"],
        ),
    ]

    CreatedAt = CommonFieldTypes.Timestamp

    Id = CommonFieldTypes.UUID

    Slug = Annotated[
        str,
        Field(
            title="Application Slug",
            pattern=r"^[a-z0-9][a-z0-9_-]{1,48}[a-z0-9]$",
            min_length=3,
            max_length=50,
            description="Normalized application identifier",
            examples=["my-app", "user-service", "api_gateway", "service123"],
        ),
    ]


class AppCreate(BaseModel):
    """Schema for creating a new application."""

    name: AppFieldTypes.AppName
    slug: AppFieldTypes.Slug


class AppCreateResponse(BaseModel):
    """Schema for application response."""

    id: AppFieldTypes.Id


class AppDelete(BaseModel):
    """Schema for deleting an application."""

    id: AppFieldTypes.Id
    slug: AppFieldTypes.Slug


class AppDeleteResponse(BaseModel):
    """Schema for application deletion response."""

    name: AppFieldTypes.AppName
