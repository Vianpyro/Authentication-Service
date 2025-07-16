from uuid import UUID

from fastapi import APIRouter, Depends, status

from ..controllers import get_application_controller as get_app_controller
from ..controllers.application import ApplicationController as AppController
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
async def get_applications(app_id: UUID, controller: AppController = Depends(get_app_controller)):
    return await controller.get_application_by_id(app_id)


@router.post("/register", response_model=AppCreateResponse, status_code=status.HTTP_201_CREATED)
async def register_application(payload: AppCreate, controller: AppController = Depends(get_app_controller)):
    return await controller.create_application(payload)


@router.patch("", response_model=AppUpdateResponse)
async def update_application(payload: AppUpdate, controller: AppController = Depends(get_app_controller)):
    return await controller.update_application(payload)


@router.delete("/{app_id}", response_model=AppDeleteResponse)
async def delete_application(app_id: UUID, controller: AppController = Depends(get_app_controller)):
    return await controller.delete_application(app_id)
