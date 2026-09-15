from app.repositories.report_repository import ReportRepository
from app.schemas.report import ReportCreate, ReportResponse


class ReportService:
    """Application service for medical report operations."""

    def __init__(self, repository: ReportRepository) -> None:
        self.repository = repository

    async def create_report(
        self,
        report: ReportCreate,
    ) -> ReportResponse:
        """Create a report record."""

        document = await self.repository.create(
            filename=report.filename,
        )

        return ReportResponse(
            report_id=str(document["_id"]),
            filename=document["filename"],
            status=document["status"],
        )