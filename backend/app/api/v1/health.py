from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
async def health_check() -> dict[str, str]:
    """
    Lightweight health-check endpoint.

    Used by Render and external uptime monitors to verify
    that the FastAPI service is responding.
    """
    return {
        "status": "ok",
    }