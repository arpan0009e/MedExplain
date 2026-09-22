import logging
from functools import lru_cache

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.ingestion.pdf_extractor import extract_text_from_pdf
from app.ingestion.text_cleaner import clean_text
from app.repositories.report_repository import ReportRepository
from app.schemas.explanation import (
    ExplanationSource,
    ReportExplanationRequest,
    ReportExplanationResponse,
)
from app.schemas.report import (
    ReportCreate,
    ReportDetailResponse,
    ReportResponse,
    ReportUploadResponse,
)
from app.services.explanation import ExplanationService
from app.services.report_service import ReportService


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


report_repository = ReportRepository()
report_service = ReportService(report_repository)


@lru_cache(maxsize=1)
def get_explanation_service() -> ExplanationService:
    """Return a shared explanation service instance."""

    return ExplanationService()


MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB


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


@router.post(
    "/upload",
    response_model=ReportUploadResponse,
)
async def upload_report(
    file: UploadFile = File(...),
) -> ReportUploadResponse:
    """
    Upload a PDF medical report, extract its text,
    clean the text, and persist the processed report.
    """

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are supported.",
        )

    file_content = await file.read(MAX_PDF_SIZE + 1)

    if len(file_content) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="PDF file size must not exceed 10 MB.",
        )

    if not file_content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is not a valid PDF.",
        )

    try:
        extracted_text, page_count = extract_text_from_pdf(
            file_content
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    cleaned_text = clean_text(extracted_text)

    if not cleaned_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The PDF contains no extractable text.",
        )

    try:
        document = await report_service.create_uploaded_report(
            filename=file.filename or "unknown.pdf",
            page_count=page_count,
            extracted_text=cleaned_text,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ReportUploadResponse(
        report_id=str(document["_id"]),
        filename=document["filename"],
        page_count=document["page_count"],
        text=document["extracted_text"],
    )


@router.post(
    "/{report_id}/explain",
    response_model=ReportExplanationResponse,
)
async def explain_report(
    report_id: str,
    request: ReportExplanationRequest,
) -> ReportExplanationResponse:
    """
    Generate an explanation based on a stored medical report
    and the user's question.
    """

    try:
        report = await report_service.get_report(report_id)

        explanation_service = get_explanation_service()

        result = await explanation_service.explain_report(
            user_question=request.question,
            report_text=report.text,
        )

        unique_sources: list[ExplanationSource] = []
        seen_sources: set[tuple[str, str, str]] = set()

        for chunk in result.sources:
            source = ExplanationSource(
                title=chunk.metadata.get("title", "Unknown"),
                source=chunk.metadata.get("source", "Unknown"),
                source_url=chunk.metadata.get("source_url", ""),
            )

            source_key = (
                source.title,
                source.source,
                source.source_url,
            )

            if source_key not in seen_sources:
                seen_sources.add(source_key)
                unique_sources.append(source)

        return ReportExplanationResponse(
            report_id=report.report_id,
            answer=result.answer,
            sources=unique_sources,
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Failed to generate explanation for report %s.",
            report_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate the medical explanation.",
        ) from exc


@router.get(
    "/{report_id}",
    response_model=ReportDetailResponse,
)
async def get_report(
    report_id: str,
) -> ReportDetailResponse:
    """Retrieve a stored medical report by ID."""

    return await report_service.get_report(report_id)