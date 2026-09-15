from fastapi import APIRouter

from app.core.database import get_database


router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return the health status of the API and database."""

    database = get_database()

    await database.command("ping")

    return {
        "status": "healthy",
        "database": "connected",
    }