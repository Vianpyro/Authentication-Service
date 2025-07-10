from app.utility.authentication import create_login_session, create_mfa_challenge_session
from app.utility.database import get_db
from app.utility.security.encryption import decrypt_field, encrypt_field
from app.utility.security.hashing import hash_field
from app.utility.security.mfa import verify_otp
from app.utility.security.tokens import hash_token
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pyotp import random_base32 as generate_otp_secret
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ....schemas.totp_secret import TOTPSecretChallengeRequest, TOTPSecretSetupRequest, TOTPSecretSetupResponse
from ....schemas.user import UserLoginResponse

router = APIRouter()


@router.post(
    "/setup",
    status_code=status.HTTP_200_OK,
    response_model=TOTPSecretSetupResponse,
    response_description="TOTP secret setup successful, returns TOTP secret and challenge token for confirmation",
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
async def confirm_2fa(
    request_body: TOTPSecretChallengeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(None, alias="Authorization"),
    mfa_challenge: str = Header(None, alias="X-TOTP-Challenge"),
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
    # Validate the presence of the Authorization header
    # TODO: Use an actual authentication middleware to handle this
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid format",
        )

    # Extract the Bearer token from the Authorization header
    access_token = authorization.split(" ", 1)[1]

    # Extract the Bearer token from the X-TOTP-Challenge header
    if not mfa_challenge or not mfa_challenge.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Challenge header missing or invalid format",
        )

    challenge_token = mfa_challenge.split(" ", 1)[1]

    try:
        result = await db.execute(
            text("SELECT * FROM get_totp_secret(p_token_hash => :p_token_hash)"),
            {"p_token_hash": hash_token(challenge_token)},
        )
        data = result.fetchone()
    except DBAPIError as e:
        if "TOTP token not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="TOTP token not found or expired",
            )

    if not data or not data.secret_encrypted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TOTP secret not found for user",
        )

    if not verify_otp(decrypt_field(data.secret_encrypted), request_body.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code",
        )

    result = await db.execute(
        text("SELECT get_email_verification_status(p_app_id => :p_app_id, p_user_id => :p_user_id)"),
        {"p_app_id": data.app_id, "p_user_id": data.user_id},
    )
    user_data = result.fetchone()

    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Create session and refresh tokens for the opaque token flow
    access_token, refresh_token = await create_login_session(data.user_id, db, data.app_id, request)
    return UserLoginResponse(
        access_token=access_token,
        id=data.user_id,
        is_email_verified=user_data[0],
        is_2fa_enabled=True,
        refresh_token=refresh_token,
    )
