"""
Base module for the API version 1 routes.
"""

from fastapi import FastAPI

from .endpoints.application import router as application_router
from .endpoints.authentication.login import router as user_authentication
from .endpoints.authentication.register import router as user_registration

__version__ = "0.1.3"

api = FastAPI(title="Authentication API", version=__version__)

api.include_router(application_router, prefix="/app", tags=["Application"])
api.include_router(user_authentication, prefix="/auth", tags=["Authentication"])
api.include_router(user_registration, prefix="/auth", tags=["Authentication"])
