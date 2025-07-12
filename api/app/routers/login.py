from typing import Union

from fastapi import APIRouter, Depends, Request, status

from ..controllers.authentication import AuthController
from ..schemas.user import UserLogin2faResponse, UserLoginRequest, UserLoginResponse

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Union[UserLoginResponse, UserLogin2faResponse],
    response_description="User logged in successfully",
)
async def login_user(request_body: UserLoginRequest, request: Request, controller: AuthController = Depends()):
    return await controller.login(request_body, request)
