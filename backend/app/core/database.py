from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi

from app.core.config import settings


client: AsyncMongoClient | None = None
database = None


async def initialize_database() -> None:
    """Create the MongoDB client, verify connectivity, and initialize indexes."""

    global client, database

    client = AsyncMongoClient(
        settings.mongodb_uri,
        server_api=ServerApi(
            version="1",
            strict=True,
            deprecation_errors=True,
        ),
    )

    database = client[settings.mongodb_database]

    await database.command("ping")

    await database.reports.create_index(
        [("status", 1), ("created_at", -1)],
        name="status_created_at_idx",
    )


async def close_database() -> None:
    """Close the MongoDB client."""

    global client, database

    if client is not None:
        await client.close()

    client = None
    database = None


def get_database():
    """Return the initialized MongoDB database."""

    if database is None:
        raise RuntimeError("Database has not been initialized.")

    return database