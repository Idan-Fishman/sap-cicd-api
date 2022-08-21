from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app import crud, deps, models, schemas
from app.config import settings


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
) -> list[models.Branch]:
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
) -> models.Branch:
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
) -> models.Branch:
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
) -> models.Branch:
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
) -> models.Branch:
    branch = await crud.branch.read_or_404(session=session, obj_id=branch_id)
    if branch.change_requests:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can not delete this branch because it contains change requests, If you "
            "wish to delete this branch, delete the change requests or move them to another branch "
            "and try again.",
        )
    await crud.branch.delete(session, db_obj=branch)
    return branch


@router.patch(
    "/{target_branch_id}/move-change-requests/{source_branch_id}",
    response_model=list[schemas.Branch],
    response_model_exclude_none=True,
)
async def move_change_requests(
    target_branch_id: UUID,
    source_branch_id: UUID,
    change_requests_numbers: list[str],
    session: AsyncSession = Depends(deps.get_session),
) -> list[models.Branch]:
    target_branch = await crud.branch.read_or_404(session=session, obj_id=target_branch_id)
    source_branch = await crud.branch.read_or_404(session=session, obj_id=source_branch_id)
    # FIXME: Lookup only for ChangeRequest.number -> soruce_branch.change_requests = ['','','']
    source_branch_change_requests_numbers = [cr.number for cr in source_branch.change_requests]

    missing_change_requests = []
    for change_request_number in change_requests_numbers:
        if not change_request_number in source_branch_change_requests_numbers:
            missing_change_requests.append(change_request_number)
    if missing_change_requests:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"the branch {source_branch.title} does not contain the following change "
            f"requests: {missing_change_requests}",
        )

    await crud.change_request.bulk_update_branch_id(
        session=session,
        source_branch_id=source_branch_id,
        target_branch_id=target_branch_id,
        objs_ids=change_requests_numbers,
    )
    await session.refresh(target_branch)
    await session.refresh(source_branch)

    return [target_branch, source_branch]
