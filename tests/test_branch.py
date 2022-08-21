import pytest
import pytest_asyncio
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas


data = {
    "branch1": {
        "title": "Refactor delete many change requests performance issue",
        "description": "Currently we are deleting change requests by looping a sql DELETE query, "
        "so we are opening and closing session to the database for each delete "
        "query. Refactor it to single sql DELETE query which deletes all the change "
        "requests using single database session.",
    },
    "branch2": {
        "title": "Add Queue table to manage the import queue to SAP systems",
        "description": "Create a queue entity the represents the import queue to a target system "
        "(SAP SYSTEM).",
    },
    "branch3": {
        "title": "Add support for moving ChangeRequests between Branches",
        "description": "Create bulk update branch_id function, that updates many change requests "
        "with single SQL query.",
    },
    "change_request1": {
        "number": "CD1K9A7D7S",
        "status": "D",
        "description": "BC-Fishman-CICD Workbench Testing CR",
        "type": "K",
    },
    "change_request2": {
        "number": "CD1L9A7D7L",
        "status": "D",
        "description": "BC-Fishman-CICD TransportOfCopies Testing CR",
        "type": "T",
    },
}


@pytest_asyncio.fixture(scope="function")
async def empty_branches(session: AsyncSession) -> list[schemas.Branch]:
    _branches = []
    branch = schemas.Branch.from_orm(
        await crud.branch.create(session=session, in_obj=schemas.BranchCreate(**data["branch1"]))
    )
    _branches.append(branch)
    branch = schemas.Branch.from_orm(
        await crud.branch.create(session=session, in_obj=schemas.BranchCreate(**data["branch2"]))
    )
    _branches.append(branch)
    return _branches


@pytest_asyncio.fixture(scope="function")
async def branch(session: AsyncSession) -> schemas.Branch:
    branch = await crud.branch.create(
        session=session, in_obj=schemas.BranchCreate(**data["branch3"])
    )
    session.add(models.ChangeRequest(**data["change_request1"], branch_id=branch.id))
    session.add(models.ChangeRequest(**data["change_request2"], branch_id=branch.id))
    await session.commit()
    await session.refresh(branch)
    return schemas.Branch.from_orm(branch)


@pytest.mark.asyncio
async def test_create_branch_returns_new_branch(client: AsyncClient, session: AsyncSession):
    # Act
    response = await client.post(url="/branches/", json=data["branch1"])
    # Assert
    assert response.status_code == 201
    body = response.json()
    assert "id" in body.keys()
    assert body["title"] == data["branch1"]["title"]
    assert body["description"] == data["branch1"]["description"]
    db_branches = await crud.branch.read_many(session=session)
    assert len(db_branches) == 1


@pytest.mark.asyncio
async def test_create_branch_non_unique_title_fails(
    client: AsyncClient,
    empty_branches: list[schemas.Branch],
):
    # Arrange
    payload = {
        "title": empty_branches[0].title,
        "description": empty_branches[1].description,
    }
    # Act
    response = await client.post(url="/branches/", json=payload)
    # Assert
    assert response.status_code == 400
    body = response.json()
    assert body == {
        "detail": {
            "loc": ["body", "title"],
            "msg": "value already exists",
        }
    }


@pytest.mark.asyncio
async def test_read_branches_returns_branches(
    client: AsyncClient, empty_branches: list[schemas.Branch]
):
    # Act
    response = await client.get(url="/branches/")
    # Assert
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2


@pytest.mark.asyncio
async def test_read_branch_returns_branch(
    client: AsyncClient, empty_branches: list[schemas.Branch]
):
    # Assert
    branch_id = empty_branches[0].id
    # Act
    response = await client.get(f"/branches/{branch_id}")
    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == empty_branches[0].title
    assert body["description"] == empty_branches[0].description


@pytest.mark.asyncio
async def test_update_branch_returns_updated_branch(
    client: AsyncClient,
    empty_branches: list[schemas.Branch],
):
    # Arrange
    branch_id = empty_branches[0].id
    payload = {"title": "Hotfix delete many change requests using single database connection"}
    # Act
    response = await client.patch(url=f"/branches/{branch_id}", json=payload)
    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == payload["title"]


@pytest.mark.asyncio
async def test_update_branch_non_unique_title_fails(
    client: AsyncClient,
    empty_branches: list[schemas.Branch],
):
    # Arrange
    branch_id = empty_branches[0].id
    payload = {"title": empty_branches[1].title}
    # Act
    response = await client.patch(url=f"/branches/{branch_id}", json=payload)
    # Assert
    assert response.status_code == 400
    body = response.json()
    assert body == {
        "detail": {
            "loc": ["body", "title"],
            "msg": "value already exists",
        }
    }


@pytest.mark.asyncio
async def test_delete_empty_branch_returns_deleted_branch(
    client: AsyncClient,
    empty_branches: list[schemas.Branch],
):
    # Arrange
    branch_id = empty_branches[0].id
    # Act
    response = await client.delete(f"/branches/{branch_id}")
    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body == jsonable_encoder(empty_branches[0])


@pytest.mark.asyncio
async def test_delete_non_empty_branch_fails(
    client: AsyncClient,
    branch: list[schemas.Branch],
):
    # Act
    response = await client.delete(f"/branches/{branch.id}")
    # Assert
    assert response.status_code == 400
    body = response.json()
    assert body == {
        "detail": "You can not delete this branch because it contains change requests, If you "
        "wish to delete this branch, delete the change requests or move them to other branch "
        "and try again."
    }


@pytest.mark.asyncio
async def test_move_change_requests_between_branches_returns_changed_branches(
    client: AsyncClient,
    branch: schemas.Branch,
    empty_branches: list[schemas.Branch],
):
    # Arrange
    target_branch_id = empty_branches[0].id
    source_branch_id = branch.id
    payload = [
        data["change_request1"]["number"],
        data["change_request2"]["number"],
    ]
    # Act
    response = await client.patch(
        url=f"/branches/{target_branch_id}/move-change-requests/{source_branch_id}",
        json=payload,
    )
    # Assert
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    target_branch = body[0]
    source_branch = body[1]
    assert len(target_branch["change_requests"]) == 2
    assert len(source_branch["change_requests"]) == 0


@pytest.mark.asyncio
async def test_move_change_requests_not_exists_between_branches_fails(
    client: AsyncClient,
    branch: schemas.Branch,
    empty_branches: list[schemas.Branch],
):
    # Arrange
    target_branch_id = empty_branches[0].id
    source_branch_id = branch.id
    source_branch_title = branch.title
    payload = [
        data["change_request1"]["number"],
        "I-DO-NOT-EXIST",
    ]
    # Act
    response = await client.patch(
        url=f"/branches/{target_branch_id}/move-change-requests/{source_branch_id}",
        json=payload,
    )
    # Assert
    assert response.status_code == 400
    body = response.json()
    body == {
        "detail": f"the branch {source_branch_title} does not contain the following change "
        f"requests: ['I-DO-NOT-EXIST']",
    }
