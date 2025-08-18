"""
This is the main entry point for the API application.
It sets up the FastAPI application, includes the home router, and mounts versioned APIs.
"""

import os
from datetime import timedelta

from app.v1 import api as v1
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI(title="Authentication API")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])


# Home - non-versioned because it is the main entry point
@app.get("/", tags=["Home"])
async def home():
    """
    Home endpoint for the API.
    Returns a simple message indicating the API is running.
    """
    return {"message": "Welcome to the Authentication API!"}


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = f"max-age={timedelta(days=365).total_seconds()}; includeSubDomains"
    return response


# API versions to make sure applications using the API won't break when the API changes
app.mount("/api/v1", v1, name="v1")


def validate_environment():
    required_vars = required_vars = [
        "AES_SECRET_KEY",
        "PASSWORD_PEPPER",
        "TOKEN_PEPPER",
        "MAIL_USERNAME",
        "MAIL_PASSWORD",
        "MAIL_SERVER",
    ]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {missing}")


if __name__ == "__main__":
    validate_environment()

    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
