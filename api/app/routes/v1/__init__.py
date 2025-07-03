"""
Base module for the API version 1 routes.
"""

from fastapi import FastAPI

from .endpoints.application import router as app_router

__version__ = "1.0.1"

api = FastAPI(title="Authentication API", version=__version__)

api.include_router(app_router, prefix="/app", tags=["Application"])
