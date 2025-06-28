"""
Application endpoints for the API.

This module provides FastAPI endpoints for registering applications in the authentication database.
"""

from app.routes.v1.schemas.application import (
    AppCreate,
    AppCreateResponse,
    AppDeleteResponse,
)
from app.utility.database import get_db
from fastapi import APIRouter, Depends, status
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
    # Call the register_app database function
    result = await db.execute(
        text("SELECT register_app(:slug, :app_name)"),
        {"slug": application.slug, "app_name": application.app_name},
    )
    app_id = result.scalar()
    await db.commit()
    return {"id": app_id}


@router.delete(
    "/{app_id}",
    status_code=status.HTTP_200_OK,
    response_model=AppDeleteResponse,
)
async def delete_application(app_id: int, db: AsyncSession = Depends(get_db)):
    "Delete an application from the authentication database."
    result = await db.execute(
        text("SELECT delete_app(:app_id)"),
        {"app_id": app_id},
    )
    app_slug = result.scalar()
    await db.commit()
    return {"slug": app_slug}
