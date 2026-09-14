from fastapi import FastAPI

app = FastAPI(
    title="MedExplain API",
    description="Backend API for the MedExplain medical report explanation platform.",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Return the health status of the API."""
    return {"status": "healthy"}