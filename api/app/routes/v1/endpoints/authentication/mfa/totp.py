from app.utility.authentication import create_login_session, create_mfa_challenge_session
from app.utility.database import get_db
from app.utility.security import encrypt_field, hash_field, hash_token
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pyotp import random_base32 as generate_otp_secret
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ....schemas.totp_secret import TOTPSecretChallengeRequest, TOTPSecretSetupRequest, TOTPSecretSetupResponse
from ....schemas.user import UserLoginResponse

router = APIRouter()


@router.post(
    "/setup",
    status_code=status.HTTP_200_OK,
    response_model=TOTPSecretSetupResponse,
    response_description="TOTP secret setup",
)
async def setup_totp_secret(request_body: TOTPSecretSetupRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Setup TOTP secret for a user.

    This endpoint is used to initiate the setup of a TOTP secret for a user.
    It is typically called when a user opts to enable two-factor authentication (2FA).

    Args:
        request_body: Request data containing the user's app ID and user ID
        request: The HTTP request object to extract client information
        db: Database session dependency

    Returns:
        TOTPSecretSetupRequest: Response containing the TOTP secret setup details

    Raises:
        HTTPException: If setup fails or user is not found
    """
    otp_secret = generate_otp_secret()

    try:
        await db.execute(
            text(
                """CALL insert_totp_secret(
                    p_user_id => :user_id,
                    p_secret_encrypted => :secret_encrypted,
                    p_secret_hash => :secret_hash,
                    p_key_version => :key_version
                )"""
            ),
            {
                "user_id": request_body.user_id,
                "secret_encrypted": encrypt_field(otp_secret),
                "secret_hash": hash_field(otp_secret, request_body.app_id),
                "key_version": 1,
            },
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP setup failed",
        )

    await db.commit()

    # TODO: Generate the QR code URL and QR code for the user to scan
    # otpauth://totp/AppName:UserEmail?secret=otp_secret&issuer=AppName
    mfa_access_token = await create_mfa_challenge_session(request_body.user_id, db, request_body.app_id, request)

    return TOTPSecretSetupResponse(secret=otp_secret, challenge_token=mfa_access_token)


@router.post(
    "/challenge",
    status_code=status.HTTP_200_OK,
    response_model=UserLoginResponse,
    response_description="User confirmed 2FA successfully",
)
async def confirm_2fa(request_body: TOTPSecretChallengeRequest, request: Request, db: AsyncSession = Depends(get_db)):
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
        text("SELECT * FROM get_totp_secret(p_token_hash => :p_token_hash)"),
        {"p_token_hash": hash_token(request_body.token)},
    )
    data = result.scalar_one_or_none()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TOTP secret not found for user",
        )

    if not data.verify(request_body.totp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code",
        )

    # Convert to response model for adding tokens
    user_dict = dict(data._mapping) if hasattr(data, "_mapping") else dict(data)

    # Create session and refresh tokens for the opaque token flow
    access_token, refresh_token = await create_login_session(request_body.user_id, db, request_body.app_id, request)
    user_dict.update({"access_token": access_token, "refresh_token": refresh_token})
    return UserLoginResponse.model_validate(user_dict)
