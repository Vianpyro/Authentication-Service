from app.services.authentication import AuthService
from app.utils.database import get_db
from app.utils.security.encryption import decrypt_field, encrypt_field
from app.utils.security.hashing import hash_field
from app.utils.security.mfa import verify_otp
from app.utils.security.tokens import require_access_token, require_challenge_token
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pyotp import random_base32 as generate_otp_secret
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.totp_secret import TOTPSecretChallengeRequest, TOTPSecretSetupRequest, TOTPSecretSetupResponse
from ..schemas.user import UserLoginResponse

router = APIRouter()


@router.post(
    "/setup",
    status_code=status.HTTP_200_OK,
    response_model=TOTPSecretSetupResponse,
    response_description="TOTP secret setup successful, returns TOTP secret and challenge token for confirmation",
)
async def setup_totp_secret(
    request_body: TOTPSecretSetupRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_session=Depends(require_access_token),
):
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
    mfa_access_token = await AuthService.create_mfa_challenge_session(
        request_body.user_id, db, request_body.app_id, request
    )

    return TOTPSecretSetupResponse(secret=otp_secret, challenge_token=mfa_access_token)


@router.post(
    "/challenge",
    status_code=status.HTTP_200_OK,
    response_model=UserLoginResponse,
    response_description="User confirmed 2FA successfully",
)
async def confirm_2fa(
    request_body: TOTPSecretChallengeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_session=Depends(require_access_token),
    challenge_data=Depends(require_challenge_token),
):
    """
    Confirm 2FA for a user.

    This endpoint is used to confirm the second factor authentication (2FA) for a user.
    It is typically called after the user has provided their TOTP code.

    Args:
        request_body: Request data containing the user's app_id and TOTP code
        request: The HTTP request object to extract client information
        db: Database session dependency
        authorization: Authorization header containing the Bearer token

    Returns:
        UserLoginResponse: Response containing user details upon successful confirmation

    Raises:
        HTTPException: If confirmation fails or user is not found
    """
    if not verify_otp(decrypt_field(challenge_data.secret_encrypted), request_body.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code",
        )

    if not challenge_data.confirmed_at:
        await db.execute(
            text("CALL confirm_totp_secret(p_totp_secret_id => :totp_secret_id)"),
            {"totp_secret_id": challenge_data.totp_secret_id},
        )
        await db.commit()

    result = await db.execute(
        text(
            "SELECT get_email_verification_status(p_app_id => :p_app_id, p_user_id => :p_user_id) AS is_email_verified"
        ),
        {"p_app_id": challenge_data.app_id, "p_user_id": challenge_data.user_id},
    )
    user_data = result.fetchone()

    # Create session and refresh tokens for the opaque token flow
    session = await AuthService.create_login_session(challenge_data.user_id, db, challenge_data.app_id, request)

    # Create response
    response_data = UserLoginResponse.model_validate(
        {
            **user_data._asdict(),
            "is_2fa_enabled": True,
            "id": challenge_data.user_id,
        }
    ).model_dump()
    response = JSONResponse(content=jsonable_encoder(response_data))

    # Attach secure cookies
    response.set_cookie(
        key="access_token",
        value=session["access_token"],
        httponly=True,
        secure=True,
        samesite="Strict",
        expires=session["access_token_expires_at"],
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=session["refresh_token"],
        httponly=True,
        secure=True,
        samesite="Strict",
        expires=session["refresh_token_expires_at"],
        path="/auth/refresh",
    )

    return response
