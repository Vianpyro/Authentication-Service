from app.utility.database import get_db
from app.utility.security.password import hash_password
from app.utility.security.tokens import hash_token
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.pending_user import (
    RegisterConfirmationRequest,
    RegisterConfirmationResponse,
)

router = APIRouter()
MIN_RESPONSE_TIME_SECONDS = 0.45


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterConfirmationResponse,
    response_description="User account created successfully",
)
async def confirm_pending_user(
    request_body: RegisterConfirmationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(None, alias="Authorization"),
):
    """
    Complete user registration by validating verification token and creating user account.

    This endpoint completes the two-step registration process by:
    1. Validating the verification token and checking expiration
    2. Creating the user account with the provided password
    3. Cleaning up the pending user record and token
    4. Returning the new user ID

    The endpoint performs comprehensive validation including token validity,
    expiration checks, and duplicate user detection.
    All validation errors are mapped to appropriate HTTP status codes.

    Args:
        pending_user: Confirmation data including app_id, token, and password
        request: HTTP request object for extracting client metadata
        db: Database session dependency

    Returns:
        PendingUserConfirmationResponse: Contains the newly created user ID

    Raises:
        HTTPException:
            - 404 Not Found: Invalid or expired verification token
            - 409 Conflict: User account already exists
            - 410 Gone: Token or registration has expired
            - 500 Internal Server Error: Unexpected database errors

    Security Features:
        - Verification token validation with cryptographic security
        - Password hashing using Argon2ID algorithm
        - Automatic cleanup of expired tokens and registrations
        - Client IP and user agent logging for audit trails
        - Atomic database operations to prevent race conditions
    """

    # Define error mappings for cleaner exception handling
    error_mappings = {
        "Pending user not found": (
            status.HTTP_404_NOT_FOUND,
            "Invalid or expired verification token",
        ),
        "Invalid verification token": (
            status.HTTP_404_NOT_FOUND,
            "Invalid verification token",
        ),
        "Token has expired": (
            status.HTTP_410_GONE,
            "Verification token has expired",
        ),
        "Registration has expired": (
            status.HTTP_410_GONE,
            "Registration has expired",
        ),
        "User already exists": (
            status.HTTP_409_CONFLICT,
            "User account already exists",
        ),
    }

    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid format",
        )

    token = authorization.split(" ", 1)[1]

    try:
        result = await db.execute(
            text(
                """
                SELECT confirm_pending_user(
                    p_app_id => :app_id,
                    p_token_hash => :token_hash,
                    p_password => :password,
                    p_ip_address => :ip_address,
                    p_user_agent => :user_agent
                )"""
            ),
            {
                "app_id": request_body.app_id,
                "token_hash": hash_token(token),
                "password": hash_password(request_body.password),
                "ip_address": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent", ""),
            },
        )
        await db.commit()

        return RegisterConfirmationResponse(user_id=result.scalar())

    except Exception as e:
        error_str = str(e)

        # Check for known database errors
        for error_msg, (status_code, detail) in error_mappings.items():
            if error_msg in error_str:
                raise HTTPException(status_code=status_code, detail=detail)

        # Re-raise unknown exceptions
        raise
