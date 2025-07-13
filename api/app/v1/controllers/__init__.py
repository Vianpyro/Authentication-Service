from app.utility.database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .application import ApplicationController


def get_application_controller(db: AsyncSession = Depends(get_db)) -> ApplicationController:
    return ApplicationController(db)
