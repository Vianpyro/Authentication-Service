from uuid import UUID

from app.utility.database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..controllers.application import ApplicationController
from ..schemas.application import (
    AppCreate,
    AppCreateResponse,
    AppDeleteResponse,
    AppGetResponse,
    AppUpdate,
    AppUpdateResponse,
)

router = APIRouter()


@router.get("/{app_id}", response_model=AppGetResponse)
async def get_applications(app_id: UUID, db: AsyncSession = Depends(get_db)):
    controller = ApplicationController(db)
    return await controller.get_application_by_id(app_id)


@router.post("/register", response_model=AppCreateResponse, status_code=201)
async def register_application(payload: AppCreate, db: AsyncSession = Depends(get_db)):
    controller = ApplicationController(db)
    return await controller.create_application(payload)


@router.patch("", response_model=AppUpdateResponse)
async def update_application(payload: AppUpdate, db: AsyncSession = Depends(get_db)):
    controller = ApplicationController(db)
    return await controller.update_application(payload)


@router.delete("/{app_id}", response_model=AppDeleteResponse)
async def delete_application(app_id: UUID, db: AsyncSession = Depends(get_db)):
    controller = ApplicationController(db)
    return await controller.delete_application(app_id)
