from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import ChangeRequest
from app.schemas import ChangeRequestCreate, ChangeRequestUpdate
from .base import BaseCRUD


class ChangeRequestCRUD(BaseCRUD[ChangeRequest, ChangeRequestCreate, ChangeRequestUpdate]):
    async def create(
        self,
        session: AsyncSession,
        in_obj: ChangeRequestCreate,
        branch_id: UUID,
    ) -> ChangeRequest:
        in_obj_data = jsonable_encoder(in_obj)
        db_obj = self.model(**in_obj_data, branch_id=branch_id)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def read_with_branch_id(
        self,
        session: AsyncSession,
        obj_id: str,
        branch_id: UUID,
    ) -> Optional[ChangeRequest]:
        statement = select(self.model).where(
            self.model.number == obj_id,
            self.model.branch_id == branch_id,
        )
        result = await session.execute(statement=statement)
        return result.scalars().first()

    async def read_with_branch_id_or_404(
        self,
        session: AsyncSession,
        obj_id: str,
        branch_id: UUID,
    ) -> ChangeRequest:
        db_obj = await self.read_with_branch_id(session=session, obj_id=obj_id, branch_id=branch_id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__tablename__.capitalize()} not found",
            )
        return db_obj

    async def read_many_filter_by_branches(
        self,
        session: AsyncSession,
        branches_ids: list[UUID],
    ) -> list[ChangeRequest]:
        statement = select(self.model).where(self.model.branch_id in branches_ids)
        result = await session.execute(statement=statement)
        return result.scalars().all()

    async def bulk_update_branch_id(
        self,
        session: AsyncSession,
        source_branch_id: UUID,
        target_branch_id: UUID,
        objs_ids: list[str],
    ) -> None:
        statement = (
            update(self.model)
            .where(
                self.model.number.in_(objs_ids),
                self.model.branch_id == source_branch_id,
            )
            .values(branch_id=target_branch_id)
        )
        await session.execute(statement=statement)
        await session.commit()


change_request = ChangeRequestCRUD(model=ChangeRequest)
