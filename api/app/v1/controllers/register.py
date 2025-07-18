import time
from random import uniform as jitter

from app.utility.security.tokens import create_token
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.pending_user import RegisterRequest
from .base import BaseController


class RegisterController(BaseController):
    """Controller for registration-related operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def register(self, payload: RegisterRequest, request: Request) -> None:
        start = time.monotonic() + jitter(0, 0.1)
        verification_token = create_token()
