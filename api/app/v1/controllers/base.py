import logging
from abc import ABC
from typing import Any, Dict, Optional

from app.utility.database import get_db
from fastapi import Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class BaseController(ABC):
    """Base controller class with common functionality for all controllers."""

    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    def handle_not_found(self, entity_name: str = "Entity", detail: Optional[str] = None):
        """Handle entity not found errors consistently."""
        message = detail or f"{entity_name} not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    def handle_bad_request(self, detail: str):
        """Handle bad request errors consistently."""
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    def handle_unauthorized(self, detail: str = "Unauthorized"):
        """Handle unauthorized access consistently."""
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

    def handle_forbidden(self, detail: str = "Forbidden"):
        """Handle forbidden access consistently."""
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    def handle_conflict(self, detail: str = "Resource already exists"):
        """Handle conflict errors consistently."""
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)

    async def execute_procedure(self, procedure: str, params: Dict[str, Any]) -> Optional[Any]:
        """Execute a database procedure safely with error handling."""
        try:
            result = await self.db.execute(text(procedure), params)
            return result.scalar_one_or_none()
        except IntegrityError as e:
            logger.warning(f"Integrity error in procedure {procedure}: {e}")
            return None
        except Exception as e:
            logger.error(f"Database error in procedure {procedure}: {e}")
            raise

    async def commit_transaction(self):
        """Commit the current transaction with error handling."""
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Transaction commit failed: {e}")
            raise
