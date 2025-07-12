"""
This is the main entry point for the API.
It sets up the home router and defines the root endpoint.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["Home"])
def read_root():
    """Root endpoint that returns a welcome message."""
    return {"message": "Welcome to the Authentication API!"}
