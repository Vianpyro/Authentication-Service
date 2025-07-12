"""
This is the main entry point for the API application.
It sets up the FastAPI application, includes the home router, and mounts versioned APIs.
"""

from app.routers import router as api_router
from app.routers.home import router as home_router
from fastapi import FastAPI

app = FastAPI(title="Authentication API")

app.include_router(home_router)
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
