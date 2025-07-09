"""
Base module for the API version 1 routes.
"""

from fastapi import FastAPI

from .endpoints.application import router as application_router
from .endpoints.authentication import router as authentication

__version__ = "0.1.2"

api = FastAPI(title="Authentication API", version=__version__)

api.include_router(application_router, prefix="/app", tags=["Application"])
api.include_router(authentication, prefix="/auth", tags=["Authentication"])
