from fastapi import APIRouter, BackgroundTasks, Depends, Request, status

from ..controllers.authentication import AuthController
from ..schemas.pending_user import RegisterConfirmationRequest, RegisterRequest

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="User registration initiated successfully",
)
async def register_user(
    background_tasks: BackgroundTasks,
    request_body: RegisterRequest,
    request: Request,
    controller: AuthController = Depends(),
):
    """Register a new user and send verification email."""
    return await controller.register(background_tasks, request_body, request)


@router.post(
    "/confirm",
    status_code=status.HTTP_200_OK,
    response_description="Email confirmation successful",
)
async def confirm_email(
    background_tasks: BackgroundTasks,
    request_body: RegisterConfirmationRequest,
    request: Request,
    controller: AuthController = Depends(),
):
    """Confirm user email address."""
    return await controller.confirm_email(background_tasks, request_body, request)
