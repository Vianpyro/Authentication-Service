from typing import TypeVar


from .base import BaseRepository

T = TypeVar("T")


class UserRepository(BaseRepository):
    async def get_by_email(self, email_hash: str, app_id: int):
        return await self.execute_procedure(
            "SELECT * FROM get_user_by_email(:email_hash, :app_id)", {"email_hash": email_hash, "app_id": app_id}
        )
