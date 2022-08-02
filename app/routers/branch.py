from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app import crud, deps, schemas
from app.config import settings
from app.models import Branch


router = APIRouter(prefix="/branches")


@router.get(
    "/",
    response_model=list[schemas.Branch],
    response_model_exclude_none=True,
)
async def read_branches(
    skip: int = 0,
    limit: int = settings.PAGE_SIZE,
    session: AsyncSession = Depends(deps.get_session),
) -> list[Branch]:
    branches = await crud.branch.read_many(session=session, skip=skip, limit=limit)
    return branches


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Branch,
    response_model_exclude_none=True,
)
async def create_branch(
    branch_obj: schemas.BranchCreate,
    session: AsyncSession = Depends(deps.get_session),
) -> Branch:
    try:
        branch = await crud.branch.create(session=session, in_obj=branch_obj)
    except IntegrityError as raw_error:
        parsed_error = crud.branch.integrity_error(raw_error)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=parsed_error,
        )
    return branch


@router.get(
    "/{branch_id}",
    response_model=schemas.Branch,
    response_model_exclude_none=True,
)
async def read_branch(
    branch_id: UUID,
    session: AsyncSession = Depends(deps.get_session),
) -> Branch:
    branch = await crud.branch.read_or_404(session=session, obj_id=branch_id)
    return branch


@router.patch(
    "/{branch_id}",
    response_model=schemas.Branch,
    response_model_exclude_none=True,
)
async def update_branch(
    branch_id: UUID,
    branch_obj: schemas.BranchUpdate,
    session: AsyncSession = Depends(deps.get_session),
) -> Branch:
    branch = await crud.branch.read_or_404(session=session, obj_id=branch_id)
    try:
        branch = await crud.branch.update(
            session=session,
            db_obj=branch,
            in_obj=branch_obj,
        )
    except IntegrityError as raw_error:
        parsed_error = crud.branch.integrity_error(raw_error)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=parsed_error,
        )
    return branch


@router.delete(
    "/{branch_id}",
    response_model=schemas.Branch,
    response_model_exclude_none=True,
)
async def delete_branch(
    branch_id: UUID,
    session: AsyncSession = Depends(deps.get_session),
) -> Branch:
    branch = await crud.branch.read_or_404(session=session, obj_id=branch_id)
    branch = await crud.branch.delete(session, db_obj=branch)
    return branch
