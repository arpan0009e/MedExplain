from pathlib import Path

import pytest
from httpx import AsyncClient


SAMPLE_PDF = Path(__file__).parent / "sample_medical_report.pdf"


@pytest.mark.asyncio
async def test_upload_pdf(client: AsyncClient) -> None:
    """Uploading a valid PDF should extract and return its text."""

    with SAMPLE_PDF.open("rb") as pdf_file:
        response = await client.post(
            "/api/v1/reports/upload",
            files={
                "file": (
                    "sample_medical_report.pdf",
                    pdf_file,
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "sample_medical_report.pdf"
    assert data["page_count"] == 1
    assert "Hemoglobin: 13.5 g/dL" in data["text"]
    assert "White Blood Cell Count: 7200 /uL" in data["text"]
    assert "Platelets: 250000 /uL" in data["text"]


@pytest.mark.asyncio
async def test_upload_non_pdf_file(client: AsyncClient) -> None:
    """Uploading a non-PDF file should be rejected."""

    response = await client.post(
        "/api/v1/reports/upload",
        files={
            "file": (
                "test.txt",
                b"This is not a PDF.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Only PDF files are supported."


@pytest.mark.asyncio
async def test_upload_invalid_pdf_signature(client: AsyncClient) -> None:
    """A file claiming to be a PDF but without a valid PDF signature should be rejected."""

    response = await client.post(
        "/api/v1/reports/upload",
        files={
            "file": (
                "fake_report.pdf",
                b"This is not actually a PDF file.",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "The uploaded file is not a valid PDF."


@pytest.mark.asyncio
async def test_upload_oversized_pdf(client: AsyncClient) -> None:
    """An oversized PDF upload should be rejected."""

    oversized_content = b"%PDF-1.7\n" + b"x" * (10 * 1024 * 1024)

    response = await client.post(
        "/api/v1/reports/upload",
        files={
            "file": (
                "large_report.pdf",
                oversized_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "PDF file size must not exceed 10 MB."

from io import BytesIO
from pypdf import PdfWriter

@pytest.mark.asyncio
async def test_upload_pdf_without_extractable_text(
    client: AsyncClient,
) -> None:
    """A valid PDF with no extractable text should be rejected."""

    pdf_buffer = BytesIO()

    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    writer.write(pdf_buffer)

    response = await client.post(
        "/api/v1/reports/upload",
        files={
            "file": (
                "empty_report.pdf",
                pdf_buffer.getvalue(),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "The PDF contains no extractable text."

@pytest.mark.asyncio
async def test_uploaded_pdf_can_be_retrieved(
    client: AsyncClient,
) -> None:
    """An uploaded PDF should be persisted and retrievable by report ID."""

    with SAMPLE_PDF.open("rb") as pdf_file:
        upload_response = await client.post(
            "/api/v1/reports/upload",
            files={
                "file": (
                    "sample_medical_report.pdf",
                    pdf_file,
                    "application/pdf",
                )
            },
        )

    assert upload_response.status_code == 200

    upload_data = upload_response.json()

    assert "report_id" in upload_data

    report_id = upload_data["report_id"]

    response = await client.get(
        f"/api/v1/reports/{report_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["report_id"] == report_id
    assert data["filename"] == "sample_medical_report.pdf"
    assert data["status"] == "uploaded"
    assert data["page_count"] == 1

    assert "Hemoglobin: 13.5 g/dL" in data["text"]
    assert "White Blood Cell Count: 7200 /uL" in data["text"]
    assert "Platelets: 250000 /uL" in data["text"]