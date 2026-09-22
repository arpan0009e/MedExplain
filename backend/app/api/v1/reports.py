from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.ingestion.pdf_extractor import extract_text_from_pdf
from app.ingestion.text_cleaner import clean_text
from app.repositories.report_repository import ReportRepository
from app.schemas.report import (
    ReportCreate,
    ReportResponse,
    ReportUploadResponse,
)
from app.services.report_service import ReportService


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)

report_repository = ReportRepository()
report_service = ReportService(report_repository)

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

    # Verify that the file actually has a PDF signature.
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


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
)
async def get_report(
    report_id: str,
) -> ReportResponse:
    """Retrieve a medical report by ID."""

    return await report_service.get_report(report_id)