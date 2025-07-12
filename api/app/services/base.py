import logging
from abc import ABC
from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """Base service class with common database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_procedure(self, procedure: str, params: Dict[str, Any]) -> Optional[Any]:
        """Execute a database procedure with error handling."""
        try:
            result = await self.db.execute(text(procedure), params)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Database error in service procedure {procedure}: {e}")
            raise

    async def execute_query(self, query: str, params: Dict[str, Any]) -> Optional[Any]:
        """Execute a database query with error handling."""
        try:
            result = await self.db.execute(text(query), params)
            return result.fetchone()
        except Exception as e:
            logger.error(f"Database error in service query {query}: {e}")
            raise
