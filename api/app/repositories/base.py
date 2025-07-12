from abc import ABC
from typing import Generic, Optional, TypeVar

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_procedure(self, procedure: str, params: dict) -> Optional[T]:
        result = await self.db.execute(text(procedure), params)
        return result.fetchone()

    async def commit(self):
        await self.db.commit()


class UserRepository(BaseRepository):
    async def get_by_email(self, email_hash: str, app_id: int):
        return await self.execute_procedure(
            "SELECT * FROM get_user_by_email(:email_hash, :app_id)", {"email_hash": email_hash, "app_id": app_id}
        )


class ApplicationRepository(BaseRepository):
    async def get_by_id(self, app_id: str):
        return await self.execute_procedure("SELECT * FROM get_application(:app_id)", {"app_id": app_id})
