"""
This is the main entry point for the API application.
It sets up the FastAPI application, includes the home router, and mounts versioned APIs.
"""

from app.v1 import api as v1
from fastapi import FastAPI

app = FastAPI(title="Authentication API")


# Home - non-versioned because it is the main entry point
@app.get("/", tags=["Home"])
async def home():
    """
    Home endpoint for the API.
    Returns a simple message indicating the API is running.
    """
    return {"message": "Welcome to the Authentication API!"}


# API versions to make sure applications using the API won't break when the API changes
app.mount("/api/v1", v1, name="v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
