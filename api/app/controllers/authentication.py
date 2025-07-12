import asyncio
import time
import zoneinfo
from datetime import datetime, timezone
from random import uniform as jitter
from typing import Optional

from fastapi import BackgroundTasks, Depends, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.user import UserRepository
from ..schemas.email import RegistrationEmailSchema
from ..schemas.pending_user import RegisterConfirmationRequest, RegisterRequest
from ..schemas.user import UserLogin2faResponse, UserLoginRequest, UserLoginResponse
from ..services.authentication import AuthService
from ..utils.database import get_db
from ..utils.email.sender import send_email_background
from ..utils.security.encryption import encrypt_field as encrypt_email
from ..utils.security.hashing import hash_email
from ..utils.security.password import verify_password
from ..utils.security.tokens import create_token, hash_token
from .base import BaseController

MIN_REGISTER_RESPONSE_TIME_SECONDS = 0.45


class AuthController(BaseController):
    """Authentication controller handling login, registration, and related operations."""

    def __init__(self, db: AsyncSession = Depends(get_db)):
        super().__init__(db)
        self.auth_service = AuthService(db)
        self.user_repo = UserRepository(db)

    async def confirm_email(
        self, background_tasks: BackgroundTasks, request_body: RegisterConfirmationRequest, request: Request
    ):
        """Confirm user email address."""
        pass

    async def login(self, request_body: UserLoginRequest, request: Request):
        """Handle user login with optional MFA support."""
        # Get user data
        email_hash = hash_email(request_body.email, request_body.app_id)
        user_data = await self.user_repo.get_by_email(email_hash, request_body.app_id)

        if not user_data:
            self.handle_not_found("User")

        if not verify_password(request_body.password, user_data.password_hash):
            self.handle_bad_request("Invalid password")

        # Handle MFA or regular login
        user_dict = dict(user_data._mapping)

        if user_data.is_2fa_enabled:
            challenge_token = await self.auth_service.create_mfa_challenge_session(
                user_data.id, request_body.app_id, request
            )
            user_dict.update({"challenge_token": challenge_token})
            return UserLogin2faResponse.model_validate(user_dict)

        # Regular login
        session = await self.auth_service.create_login_session(user_data.id, request_body.app_id, request)
        user_dict.update(session)
        return UserLoginResponse.model_validate(user_dict)

    async def register(
        self,
        background_tasks: BackgroundTasks,
        request_body: RegisterRequest,
        request: Request,
    ):
        """Handle user registration with email verification."""
        start = time.monotonic() + jitter(0, 0.1)
        verification_token = create_token()

        # Register pending user
        expires_at = await self._register_pending_user(request_body, verification_token, request)

        # Ensure minimum response time for security
        await self._ensure_minimum_response_time(start)

        if expires_at is None:
            return

        await self.commit_transaction()

        # Send verification email
        await self._send_verification_email(background_tasks, request_body, verification_token, expires_at)

    async def _register_pending_user(
        self, request_body: RegisterRequest, verification_token: str, request: Request
    ) -> Optional[datetime]:
        """Register a pending user in the database."""
        procedure = """
            SELECT register_pending_user(
                p_app_id => :app_id,
                p_token_hash => :token_hash,
                p_email_encrypted => :email_encrypted,
                p_email_hash => :email_hash,
                p_ip_address => :ip_address,
                p_user_agent => :user_agent
            )
        """

        params = {
            "app_id": request_body.app_id,
            "token_hash": hash_token(verification_token),
            "email_encrypted": encrypt_email(request_body.email),
            "email_hash": hash_email(request_body.email, request_body.app_id),
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent", ""),
        }

        try:
            return await self.execute_procedure(procedure, params)
        except IntegrityError:
            # Silently handle integrity errors (e.g., duplicate email)
            return None

    async def _ensure_minimum_response_time(self, start: float):
        """Ensure minimum response time for security purposes."""
        elapsed = time.monotonic() - start
        remaining_time = max(0, MIN_REGISTER_RESPONSE_TIME_SECONDS - elapsed)
        if remaining_time:
            await asyncio.sleep(remaining_time)

    async def _send_verification_email(
        self,
        background_tasks: BackgroundTasks,
        request_body: RegisterRequest,
        verification_token: str,
        expires_at: datetime,
    ):
        """Send verification email to the user."""
        expires_at_formatted = self._format_expiration_time(expires_at, request_body.timezone)
        app_name = await self._get_application_name(request_body.app_id)

        send_email_background(
            background_tasks,
            RegistrationEmailSchema(
                recipients=[request_body.email],
                subject=f"{app_name} - Email Verification",
                body={
                    "title": app_name,
                    "confirmation_url": f"{request_body.confirmation_url}?token={verification_token}",
                    "expires_at": expires_at_formatted,
                },
                template_path="registration_email.html",
            ),
        )

    def _format_expiration_time(self, expires_at: datetime, timezone_str: Optional[str]) -> str:
        """Format expiration time based on user's timezone."""
        if isinstance(expires_at, datetime):
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if timezone_str:
                try:
                    user_tz = zoneinfo.ZoneInfo(timezone_str)
                    expires_at_local = expires_at.astimezone(user_tz)
                    tz_name = expires_at_local.strftime("%Z")
                    return expires_at_local.strftime(f"%B %d, %Y at %I:%M %p {tz_name}")
                except (zoneinfo.ZoneInfoNotFoundError, ValueError):
                    return expires_at.strftime("%B %d, %Y at %I:%M %p UTC")
            else:
                return expires_at.strftime("%B %d, %Y at %I:%M %p UTC")
        else:
            return str(expires_at)

    async def _get_application_name(self, app_id: str) -> str:
        """Get application name from database."""
        result = await self.execute_procedure("SELECT get_application_name(:app_id)", {"app_id": app_id})
        return result or "Application"
