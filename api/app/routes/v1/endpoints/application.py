"""
Application endpoints for the API.

This module provides FastAPI endpoints for registering applications in the authentication database.
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
)
async def get_applications(application: AppGet, db: AsyncSession = Depends(get_db)):
    "Retrieve all registered applications from the authentication database."
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
)
async def register_application(
    application: AppCreate, db: AsyncSession = Depends(get_db)
):
    "Register a new application in the authentication database."
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
)
async def update_application(
    application: AppUpdate, db: AsyncSession = Depends(get_db)
):
    "Update an existing application's details in the authentication database."
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
            "p_new_status": application.new_status,
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
)
async def delete_application(
    application: AppDelete, db: AsyncSession = Depends(get_db)
):
    "Delete an application from the authentication database."
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
