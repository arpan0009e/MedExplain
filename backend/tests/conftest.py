from collections.abc import AsyncGenerator

import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture(loop_scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async HTTP client with an application lifespan
    running on the same event loop as the test.
    """
    async with LifespanManager(app):
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as test_client:
            yield test_client