from fastapi import HTTPException, status

from app.repositories.report_repository import ReportRepository
from app.schemas.report import (
    ReportCreate,
    ReportDetailResponse,
    ReportResponse,
)


class ReportService:
    """Application service for medical report operations."""

    def __init__(self, repository: ReportRepository) -> None:
        self.repository = repository

    async def create_report(
        self,
        report: ReportCreate,
    ) -> ReportResponse:
        """Create a new report record."""

        document = await self.repository.create(
            filename=report.filename,
        )

        return ReportResponse(
            report_id=str(document["_id"]),
            filename=document["filename"],
            status=document["status"],
        )

    async def create_uploaded_report(
        self,
        filename: str,
        page_count: int,
        extracted_text: str,
    ) -> dict:
        """
        Persist a successfully processed PDF report.

        The extracted text should already be cleaned before
        reaching this service method.
        """

        if not filename.strip():
            raise ValueError("Filename cannot be empty.")

        if page_count <= 0:
            raise ValueError("Page count must be greater than zero.")

        if not extracted_text.strip():
            raise ValueError("Extracted report text cannot be empty.")

        return await self.repository.create_uploaded_report(
            filename=filename,
            page_count=page_count,
            extracted_text=extracted_text,
        )

    async def get_report(
        self,
        report_id: str,
    ) -> ReportDetailResponse:
        """Retrieve a stored medical report by ID."""

        document = await self.repository.get_by_id(report_id)

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found.",
            )

        return ReportDetailResponse(
            report_id=str(document["_id"]),
            filename=document["filename"],
            status=document["status"],
            page_count=document.get("page_count", 0),
            text=document.get("extracted_text", ""),
        )