from fastapi import APIRouter

from .application import router as application_router
from .login import router as login_router
from .mfa import router as mfa_router
from .register import router as register_router

router = APIRouter()

router.include_router(application_router, prefix="/app", tags=["Application"])
router.include_router(login_router, prefix="/auth/login", tags=["Authentication", "Login"])
router.include_router(mfa_router, prefix="/auth/mfa", tags=["Authentication", "Multifactor Authentication"])
router.include_router(register_router, prefix="/auth/register", tags=["Authentication", "Registration"])
