from datetime import datetime
from typing import Any, Dict

from fastapi import Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def create_login_response_with_cookies(
    response_data: Dict[str, Any], session: Dict[str, str | datetime]
) -> Response:
    """
    Create a JSON response with secure authentication cookies.

    Args:
        response_data: The response data to include in the JSON body
        session: Dictionary containing access_token, refresh_token and their expiration dates

    Returns:
        JSONResponse with secure httpOnly cookies set
    """
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
