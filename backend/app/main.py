from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import close_database, initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown resources."""

    await initialize_database()

    yield

    await close_database()


app = FastAPI(
    title=settings.app_name,
    description="Backend API for the MedExplain medical report explanation platform.",
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")