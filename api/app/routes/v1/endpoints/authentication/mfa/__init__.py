from fastapi import APIRouter

from .totp import router as totp_router

router = APIRouter()

router.include_router(totp_router, prefix="/totp", tags=["Authentication", "Multi-Factor Authentication", "TOTP"])
