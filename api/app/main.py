"""
This is the main entry point for the API application.
It sets up the FastAPI application, includes the home router, and mounts versioned APIs.
"""

from app.routes.home import router as home_router
from app.routes.v1 import api as v1
from fastapi import FastAPI

# from app.routes.v2 import api as v2

app = FastAPI(title="Authentication API")

# Home - non-versioned because it is the main entry point
app.include_router(home_router)

# API versions to make sure applications using the API won't break when the API changes
app.mount("/api/v1", v1)
# app.mount("/api/v2", v2)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
