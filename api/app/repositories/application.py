from typing import TypeVar


from .base import BaseRepository

T = TypeVar("T")


class ApplicationRepository(BaseRepository):
    async def get_by_id(self, app_id: str):
        return await self.execute_procedure("SELECT * FROM get_application(:app_id)", {"app_id": app_id})
