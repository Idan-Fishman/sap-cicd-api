from typing import List

import pytest
import pytest_asyncio
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.schemas import Branch, BranchCreate


data = {
    "branch1": {
        "title": "Refactor delete many change requests performance issue",
        "description": "Currently we are deleting change requests by looping a sql DELETE query, "
                       "so we are opening and closing session to the database for each delete "
                       "query. Refactor it to single sql DELETE query which deletes all the change "
                       "requests using single database session."
    },
    "branch2": {
        "title": "Add Queue table to manage the import queue to SAP systems",
        "description": "Create a queue entity the represents the import queue to a target system "
                       "(SAP SYSTEM)."
    },
}


@pytest_asyncio.fixture(scope="function")
async def branches(session: AsyncSession) -> List[Branch]:
    _branches = []
    branch = Branch.from_orm(
        await crud.branch.create(
            session=session,
            in_obj=BranchCreate(**data["branch1"])
        )
    )
    _branches.append(branch)
    branch = Branch.from_orm(
        await crud.branch.create(
            session=session,
            in_obj=BranchCreate(**data["branch2"])
        )
    )
    _branches.append(branch)
    return _branches


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
    branches: List[Branch],
):
    # Arrange
    payload = {
        "title": branches[0].title,
        "description": branches[1].description,
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
async def test_read_branches_returns_branches(client: AsyncClient, branches: List[Branch]):
    # Act
    response = await client.get(url="/branches/")
    # Assert
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2


@pytest.mark.asyncio
async def test_read_branch_returns_branch(client: AsyncClient, branches: List[Branch]):
    # Assert
    branch_id = branches[0].id
    # Act
    response = await client.get(f"/branches/{branch_id}")
    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == branches[0].title
    assert body["description"] == branches[0].description


@pytest.mark.asyncio
async def test_update_branch_returns_updated_branch(client: AsyncClient, branches: List[Branch]):
    # Arrange
    branch_id = branches[0].id
    payload = {"title": "Hotfix delete many change requests using single database connection"}
    # Act
    response = await client.patch(url=f"/branches/{branch_id}", json=payload)
    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == payload["title"]


@pytest.mark.asyncio
async def test_update_branch_non_unique_title_fails(client: AsyncClient, branches: List[Branch]):
    # Arrange
    branch_id = branches[0].id
    payload = {"title": branches[1].title}
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
async def test_delete_branch_returns_deleted_branch(client: AsyncClient, branches: List[Branch]):
    # Arrange
    branch_id = branches[0].id
    # Act
    response = await client.delete(f"/branches/{branch_id}")
    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body == jsonable_encoder(branches[0])
