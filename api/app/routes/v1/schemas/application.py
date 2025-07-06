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

    CreatedAt = CommonFieldTypes.NonFutureTimestamp

    Description = Annotated[
        str | None,
        Field(
            title="Application Description",
            max_length=500,
            description="Optional new description for the application",
            examples=["Updated description of the application"],
        ),
    ]

    Description = Annotated[
        str | None,
        Field(
            title="Application Description",
            max_length=500,
            description="Optional new description for the application",
            examples=["Updated description of the application"],
        ),
    ]

    Id = CommonFieldTypes.UUID

    IsActive = Annotated[
        bool,
        Field(
            title="Is Active",
            description="Indicates if the application is currently active",
            default=True,
            examples=[True, False],
        ),
    ]

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

    UpdatedAt = CommonFieldTypes.NonFutureTimestamp


class AppCreate(BaseModel):
    """Schema for creating a new application."""

    name: AppFieldTypes.AppName
    slug: AppFieldTypes.Slug
    description: AppFieldTypes.Description | None = None


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


class AppGetResponse(BaseModel):
    """Schema for retrieving application details."""

    name: AppFieldTypes.AppName
    slug: AppFieldTypes.Slug
    description: AppFieldTypes.Description | None = None
    is_active: AppFieldTypes.IsActive
    created_at: AppFieldTypes.CreatedAt
    updated_at: CommonFieldTypes.NonFutureTimestamp | None = None

    class Config:
        from_attributes = True


class AppUpdate(BaseModel):
    """Schema for updating application details."""

    id: AppFieldTypes.Id
    new_name: AppFieldTypes.AppName | None = None
    new_slug: AppFieldTypes.Slug | None = None
    new_description: AppFieldTypes.Description | None = None
    is_active: AppFieldTypes.IsActive = True


class AppUpdateResponse(BaseModel):
    """Schema for application update response."""

    name: AppFieldTypes.AppName
    slug: AppFieldTypes.Slug
    description: AppFieldTypes.Description
    is_active: AppFieldTypes.IsActive
    updated_at: AppFieldTypes.UpdatedAt

    class Config:
        from_attributes = True
