"""
Application endpoints for the API.

This module provides FastAPI endpoints for registering applications in the authentication database.
"""

from app.routes.v1.schemas.application import ApplicationCreate, ApplicationResponse
from app.utility.database import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=ApplicationResponse
)
async def register_application(
    application: ApplicationCreate, db: AsyncSession = Depends(get_db)
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
