"""
Application endpoints for the API.

This module provides FastAPI endpoints for registering applications in the authentication database.
"""

from app.routes.v1.schemas.application import (
    AppCreate,
    AppCreateResponse,
    AppDelete,
    AppDeleteResponse,
)
from app.utility.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=AppCreateResponse,
)
async def register_application(
    application: AppCreate, db: AsyncSession = Depends(get_db)
):
    "Register a new application in the authentication database."
    # Call the register_application database function
    result = await db.execute(
        text("SELECT register_application(:p_app_name, :p_app_slug)"),
        {"p_app_name": application.name, "p_app_slug": application.slug},
    )
    app_id = result.scalar()
    await db.commit()
    return {"id": app_id}


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
    return {"name": app_name}
