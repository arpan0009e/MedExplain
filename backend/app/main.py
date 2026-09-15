from fastapi import FastAPI

from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description="Backend API for the MedExplain medical report explanation platform.",
    version=settings.app_version,
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Return the health status of the API."""
    return {"status": "healthy"}