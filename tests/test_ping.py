import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ping_returns_pong(client: AsyncClient):
    response = await client.get("/ping")
    body = response.json()
    assert body == {"ping": "pong!"}
