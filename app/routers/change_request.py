from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, deps, models, schemas


router = APIRouter(prefix="/branches/{branch_id}/change-requests")


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ChangeRequest,
    response_model_exclude_none=True,
)
async def create_change_request(
    branch_id: UUID,
    change_request_obj: schemas.ChangeRequestCreate,
    session: AsyncSession = Depends(deps.get_session),
) -> models.ChangeRequest:
    await crud.branch.read_or_404(session=session, obj_id=branch_id)
    # TODO: integrate with hovav's api
    change_request = await crud.change_request.create(
        session=session,
        in_obj=change_request_obj,
        branch_id=branch_id,
    )
    return change_request


@router.get(
    "/{change_request_id}",
    response_model=schemas.ChangeRequest,
    response_model_exclude_none=True,
)
async def read_change_request(
    branch_id: UUID,
    change_request_id: str,
    session: AsyncSession = Depends(deps.get_session),
) -> models.ChangeRequest:
    await crud.branch.read_or_404(session=session, obj_id=branch_id)
    change_request = await crud.change_request.read_with_branch_id_or_404(
        session=session,
        obj_id=change_request_id,
        branch_id=branch_id,
    )
    return change_request


@router.patch(
    "/{change_request_id}",
    response_model=schemas.ChangeRequest,
    response_model_exclude_none=True,
)
async def update_change_request(
    change_request_id: UUID,
    change_request_obj: schemas.ChangeRequestUpdate,
    session: AsyncSession = Depends(deps.get_session),
) -> models.ChangeRequest:
    change_request = await crud.change_request.read_or_404(
        session=session,
        obj_id=change_request_id,
    )
    # TODO: add is cr empty validation hovav's api
    change_request = await crud.change_request.update(
        session=session,
        db_obj=change_request,
        in_obj=change_request_obj,
    )
    return change_request


@router.delete(
    "/{change_request_id}",
    response_model=schemas.ChangeRequest,
    response_model_exclude_none=True,
)
async def delete_change_request(
    change_request_id: UUID,
    session: AsyncSession = Depends(deps.get_session),
) -> models.ChangeRequest:
    change_request = await crud.change_request.read_or_4x04(
        session=session,
        obj_id=change_request_id,
    )
    # TODO: add is cr empty validation hovav's api
    change_request = await crud.change_request.delete(session, db_obj=change_request)
    return change_request
