from fastapi import APIRouter

from .email_confirm import router as email_confirm_router
from .login import router as login_router
from .register import router as register_router

router = APIRouter()

router.include_router(email_confirm_router, prefix="/confirm", tags=["Authentication", "Email Confirmation"])
router.include_router(login_router, prefix="/login", tags=["Authentication", "Login"])
router.include_router(register_router, prefix="/register", tags=["Authentication", "Registration"])
