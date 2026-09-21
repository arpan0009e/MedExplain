from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.reports import router as reports_router
from app.api.explanation import router as explanation_router


api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(reports_router)
api_router.include_router(explanation_router)