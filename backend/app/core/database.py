from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi

from app.core.config import settings


client = AsyncMongoClient(
    settings.mongodb_uri,
    server_api=ServerApi(
        version="1",
        strict=True,
        deprecation_errors=True,
    ),
)

database = client[settings.mongodb_database]


async def initialize_database() -> None:
    """Create required database indexes."""

    await database.reports.create_index(
        [("status", 1), ("created_at", -1)]
    )