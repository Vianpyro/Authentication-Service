"""
Application Management API Endpoints.

This module provides FastAPI endpoints for complete application lifecycle management in the authentication service.
Applications are the top-level entities that users register for and authenticate against.

The module supports:
- Application registration with name, slug, and description
- Retrieving application details by ID
- Updating application metadata and status
- Application deletion with verification

Features:
- Unique slug validation for application identification
- Application status management (active/inactive)
- Comprehensive error handling with appropriate HTTP status codes
- Atomic database operations for data consistency

Security Features:
- Application slug verification for delete operations
- Input validation for all application data
- Database-level constraints enforcement
"""

from app.routes.v1.schemas.application import (
    AppCreate,
    AppCreateResponse,
    AppDelete,
    AppDeleteResponse,
    AppGet,
    AppGetResponse,
    AppUpdate,
    AppUpdateResponse,
)
from app.utility.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=AppGetResponse,
    response_description="Application details retrieved successfully",
)
async def get_applications(application: AppGet, db: AsyncSession = Depends(get_db)):
    """
    Retrieve application details by application ID.

    This endpoint fetches comprehensive application information including
    metadata, status, and timestamps for a specific application ID.

    Args:
        application: Request data containing the application ID to retrieve
        db: Database session dependency

    Returns:
        AppGetResponse: Complete application details including:
            - name: Application display name
            - slug: Unique application identifier
            - description: Application description
            - is_active: Current application status
            - created_at: Application registration timestamp
            - updated_at: Last modification timestamp

    Raises:
        HTTPException:
            - 404 Not Found: Application with specified ID does not exist
    """
    result = await db.execute(
        text("SELECT * FROM applications WHERE id = :p_app_id"),
        {"p_app_id": application.id},
    )

    app_details = result.fetchone()
    if app_details is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return AppGetResponse(
        name=app_details.app_name,
        slug=app_details.slug,
        description=app_details.app_description,
        is_active=app_details.is_active,
        created_at=app_details.created_at,
        updated_at=app_details.updated_at,
    )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=AppCreateResponse,
    response_description="Application registered successfully",
)
async def register_application(
    application: AppCreate, db: AsyncSession = Depends(get_db)
):
    """
    Register a new application in the authentication system.

    This endpoint creates a new application record with the provided metadata.
    The application slug must be unique across the system and is used for
    application identification in various operations.

    Args:
        application: Registration data including name, slug, and description
        db: Database session dependency

    Returns:
        AppCreateResponse: Contains the newly created application ID

    Raises:
        HTTPException:
            - 400 Bad Request: Invalid input data or validation errors
            - 409 Conflict: Application slug already exists

    Security Features:
        - Unique slug constraint enforcement
        - Input validation and sanitization
        - Atomic database operations
    """
    result = await db.execute(
        text(
            "SELECT register_application(:p_app_name, :p_app_slug, :p_app_description)"
        ),
        {
            "p_app_name": application.name,
            "p_app_slug": application.slug,
            "p_app_description": application.description,
        },
    )
    app_id = result.scalar()
    await db.commit()
    return AppCreateResponse(id=app_id)


@router.patch(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=AppUpdateResponse,
    response_description="Application updated successfully",
)
async def update_application(
    application: AppUpdate, db: AsyncSession = Depends(get_db)
):
    """
    Update an existing application's metadata and status.

    This endpoint allows partial updates to application details including
    name, slug, description, and active status. At least one field must
    be provided for the update to proceed.

    Args:
        application: Update data with application ID and optional new values
        db: Database session dependency

    Returns:
        AppUpdateResponse: Updated application details with new timestamp

    Raises:
        HTTPException:
            - 400 Bad Request: No update fields provided
            - 404 Not Found: Application with specified ID does not exist
            - 409 Conflict: New slug conflicts with existing application

    Security Features:
        - Partial update validation
        - Unique slug constraint enforcement
        - Atomic database operations
    """
    if (
        not application.new_name
        and not application.new_slug
        and not application.new_description
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be updated",
        )

    result = await db.execute(
        text(
            "SELECT * FROM update_application(:p_id, :p_new_name, :p_new_slug, :p_new_description, :p_new_status)"
        ),
        {
            "p_id": application.id,
            "p_new_name": application.new_name,
            "p_new_slug": application.new_slug,
            "p_new_description": application.new_description,
            "p_new_status": application.is_active,
        },
    )
    app_details = result.fetchone()

    if app_details is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    await db.commit()
    return AppUpdateResponse(
        name=app_details.app_name,
        slug=app_details.slug,
        description=app_details.app_description,
        is_active=app_details.is_active,
        updated_at=app_details.updated_at,
    )


@router.delete(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=AppDeleteResponse,
    response_description="Application deleted successfully",
)
async def delete_application(
    application: AppDelete, db: AsyncSession = Depends(get_db)
):
    """
    Delete an application from the authentication system.

    This endpoint permanently removes an application and all associated data.
    Both application ID and slug must be provided for verification to prevent
    accidental deletions.

    Args:
        application: Deletion data containing both application ID and slug
        db: Database session dependency

    Returns:
        AppDeleteResponse: Name of the deleted application for confirmation

    Raises:
        HTTPException:
            - 404 Not Found: Application not found or ID/slug mismatch

    Security Features:
        - Dual verification with ID and slug
        - Cascading deletion of related data
        - Atomic database operations

    Warning:
        This operation is irreversible and will delete all associated user
        accounts, tokens, and other application-related data.
    """
    result = await db.execute(
        text("SELECT delete_application(:p_app_id, :p_app_slug)"),
        {"p_app_id": application.id, "p_app_slug": application.slug},
    )
    app_name = result.scalar()
    if app_name is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found or ID/slug mismatch",
        )
    await db.commit()
    return AppDeleteResponse(name=app_name)
