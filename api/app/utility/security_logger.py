from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def log_security_event(
    db: AsyncSession, event_type: str, app_id: UUID, user_id: UUID = None, metadata: dict = None
):
    await db.execute(
        text(
            """
            CALL insert_security_event(
                p_app_id := :app_id,
                p_user_id := :user_id,
                p_event_type := :event_type,
                p_metadata := :metadata
            )"""
        ),
        {"event_type": event_type, "metadata": metadata, "app_id": app_id, "user_id": user_id},
    )
