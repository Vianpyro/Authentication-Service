from app.utility.authentication import create_login_session
from app.utility.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ....schemas.totp_secret import TOTPSecretChallengeRequest
from ....schemas.user import UserLoginResponse

router = APIRouter()


@router.post(
    "/challenge",
    status_code=status.HTTP_200_OK,
    response_model=UserLoginResponse,
    response_description="User confirmed 2FA successfully",
)
async def confirm_2fa(totp: TOTPSecretChallengeRequest, db: AsyncSession = Depends(get_db)):
    """
    Confirm 2FA for a user.

    This endpoint is used to confirm the second factor authentication (2FA) for a user.
    It is typically called after the user has provided their TOTP code.

    Args:
        user: Request data containing the user's email, password, and TOTP code
        request: The HTTP request object to extract client information
        db: Database session dependency

    Returns:
        UserLoginResponse: Response containing user details upon successful confirmation

    Raises:
        HTTPException: If confirmation fails or user is not found
    """
    result = await db.execute(
        text(...),  # TODO
        {"p_app_id": totp.app_id, "p_token": totp.code},
    )
    data = result.scalar_one_or_none()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TOTP secret not found for user",
        )

    if not data.verify(totp.totp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code",
        )

    # Convert to response model for adding tokens
    user_dict = dict(data._mapping) if hasattr(data, "_mapping") else dict(data)

    # Create session and refresh tokens for the opaque token flow
    access_token, refresh_token = await create_login_session(totp.user_id, db, totp.app_id, totp.request)
    user_dict.update({"access_token": access_token, "refresh_token": refresh_token})
    return UserLoginResponse.model_validate(user_dict)
