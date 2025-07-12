from typing import Any, Dict

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseService


class AuthService(BaseService):
    """Authentication service handling session management."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def create_login_session(self, user_id: int, app_id: int, request: Request) -> Dict[str, Any]:
        """Create a login session for a user."""
        procedure = """
            SELECT create_login_session(
                p_user_id => :user_id,
                p_app_id => :app_id,
                p_ip_address => :ip_address,
                p_user_agent => :user_agent
            )
        """

        params = {
            "user_id": user_id,
            "app_id": app_id,
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent", ""),
        }

        result = await self.execute_procedure(procedure, params)
        return {"session_token": result} if result else {}

    async def create_mfa_challenge_session(self, user_id: int, app_id: int, request: Request) -> str:
        """Create an MFA challenge session for a user."""
        procedure = """
            SELECT create_mfa_challenge_session(
                p_user_id => :user_id,
                p_app_id => :app_id,
                p_ip_address => :ip_address,
                p_user_agent => :user_agent
            )
        """

        params = {
            "user_id": user_id,
            "app_id": app_id,
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent", ""),
        }

        result = await self.execute_procedure(procedure, params)
        return result or ""
