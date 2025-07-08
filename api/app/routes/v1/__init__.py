"""
Base module for the API version 1 routes.
"""

from fastapi import FastAPI

from .endpoints.application import router as app_router
from .endpoints.pending_user import router as pending_user_router
from .endpoints.user import router as user_router

__version__ = "0.1.2"

api = FastAPI(title="Authentication API", version=__version__)

api.include_router(app_router, prefix="/app", tags=["Application"])
api.include_router(pending_user_router, prefix="/user/register", tags=["User"])
api.include_router(user_router, prefix="/user", tags=["User"])
