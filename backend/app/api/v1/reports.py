from fastapi import APIRouter, status

from app.repositories.report_repository import ReportRepository
from app.schemas.report import ReportCreate, ReportResponse
from app.services.report_service import ReportService


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)

report_repository = ReportRepository()
report_service = ReportService(report_repository)


@router.post(
    "",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_report(
    report: ReportCreate,
) -> ReportResponse:
    """Create a new medical report record."""

    return await report_service.create_report(report)


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
)
async def get_report(
    report_id: str,
) -> ReportResponse:
    """Retrieve a medical report by ID."""

    return await report_service.get_report(report_id)