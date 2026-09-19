import asyncio

from app.core.config import settings
from app.core.database import (
    close_database,
    get_database,
    initialize_database,
)


def test_mongodb_connection():
    asyncio.run(_test_mongodb_connection())


async def _test_mongodb_connection():
    await initialize_database()

    try:
        database = get_database()

        assert database.name == settings.mongodb_database
    finally:
        await close_database()