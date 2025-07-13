from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.application import (
    AppCreate,
    AppCreateResponse,
    AppDelete,
    AppDeleteResponse,
    AppGetResponse,
    AppUpdate,
    AppUpdateResponse,
)
from .base import BaseController


class ApplicationController(BaseController):
    """Controller for application-related operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_application_by_id(self, app_id: UUID) -> AppGetResponse:
        result = await self.db.execute(text("SELECT * FROM get_application(p_app_id => :app_id)"), {"app_id": app_id})
        row = result.fetchone()
        if row is None:
            self.handle_not_found("Application")
        return AppGetResponse.model_validate(row)

    async def create_application(self, payload: AppCreate) -> AppCreateResponse:
        result = await self.db.execute(
            text("SELECT register_application(p_name => :name, p_slug => :slug, p_description => :description)"),
            payload.model_dump(),
        )
        app_id = result.scalar()
        await self.db.commit()
        return AppCreateResponse(app_id=app_id)

    async def update_application(self, payload: AppUpdate) -> AppUpdateResponse:
        if not any([payload.new_name, payload.new_slug, payload.new_description]):
            self.handle_bad_request("At least one field must be updated")

        result = await self.db.execute(
            text(
                """
                SELECT * FROM update_application(
                    p_app_id => :app_id,
                    p_new_name => :new_name,
                    p_new_slug => :new_slug,
                    p_new_description => :new_description,
                    p_new_status => :new_status
                )
            """
            ),
            payload.model_dump(),
        )
        row = result.fetchone()
        if not row:
            self.handle_not_found("Application")
        await self.db.commit()
        return AppUpdateResponse.model_validate(row)

    async def delete_application(self, payload: AppDelete) -> AppDeleteResponse:
        result = await self.db.execute(
            text("SELECT delete_application(p_app_id => :app_id, p_slug => :slug)"), payload.model_dump()
        )
        name = result.scalar_one_or_none()
        if name is None:
            self.handle_not_found("Application")
        await self.db.commit()
        return AppDeleteResponse(name=name)
