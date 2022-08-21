from typing import Union

from httpx import AsyncClient

from app import schemas
from app.config import settings


async def fetch_auth_headers_and_cookies(client: AsyncClient) -> dict[str, Union[str, list[str]]]:
    response = await client.get(
        url=settings.SAP_AUTH_URL,
        headers={
            "Authorization": settings.SAP_BASIC_AUTH_HEADER,
            "Content-Type": "application/json",
            "x-csrf-token": "fetch",
        },
    )
    credentials = {"x-csrf-token": response.headers["x-csrf-token"], "cookies": response.cookies}
    return credentials


async def create_change_request(
    client: AsyncClient,
    change_request_obj: schemas.ChangeRequestCreate,
) -> dict[str, str]:
    pass


async def edit_change_request() -> None:
    pass


async def delete_change_request() -> None:
    pass


async def fetch_change_request_content(client: AsyncClient):
    pass
