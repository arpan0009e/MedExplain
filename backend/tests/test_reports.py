from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.rag.retriever import RetrievedChunk
from app.services.explanation import ExplanationResult


SAMPLE_PDF = Path(__file__).parent / "sample_medical_report.pdf"


@pytest.mark.asyncio
async def test_create_report(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/reports",
        json={"filename": "test_report.pdf"},
    )

    assert response.status_code == 201

    data = response.json()

    assert "report_id" in data
    assert data["filename"] == "test_report.pdf"
    assert data["status"] == "uploaded"


@pytest.mark.asyncio
async def test_get_report(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/reports",
        json={"filename": "retrieval_test.pdf"},
    )

    assert create_response.status_code == 201

    report_id = create_response.json()["report_id"]

    response = await client.get(
        f"/api/v1/reports/{report_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["report_id"] == report_id
    assert data["filename"] == "retrieval_test.pdf"
    assert data["status"] == "uploaded"


@pytest.mark.asyncio
async def test_get_nonexistent_report(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/api/v1/reports/507f1f77bcf86cd799439011"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Report not found."


@pytest.mark.asyncio
async def test_get_invalid_report_id(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/api/v1/reports/not-a-valid-id"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Report not found."


@pytest.mark.asyncio
async def test_explain_uploaded_report(
    client: AsyncClient,
) -> None:
    """
    Verify that an uploaded report can be sent to the
    report-specific explanation endpoint.

    The actual ExplanationService is mocked so this test
    does not call Gemini.
    """

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

    report_id = upload_data["report_id"]

    fake_result = ExplanationResult(
        answer=(
            "Your report lists a hemoglobin value of 13.5 g/dL."
        ),
        sources=[
            RetrievedChunk(
                chunk_id="chunk-1",
                document_id="hemoglobin",
                text=(
                    "Hemoglobin is a protein in red blood cells "
                    "that carries oxygen."
                ),
                score=0.95,
                metadata={
                    "title": "Hemoglobin Test",
                    "source": "MedlinePlus",
                    "source_url": (
                        "https://medlineplus.gov/lab-tests/"
                        "hemoglobin-test/"
                    ),
                },
            )
        ],
    )

    with patch(
        "app.api.v1.reports.get_explanation_service"
    ) as mock_get_service:
        mock_service = AsyncMock()

        mock_service.explain_report.return_value = fake_result

        mock_get_service.return_value = mock_service

        response = await client.post(
            f"/api/v1/reports/{report_id}/explain",
            json={
                "question": "What does my hemoglobin result mean?"
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["report_id"] == report_id

    assert data["answer"] == (
        "Your report lists a hemoglobin value of 13.5 g/dL."
    )

    assert len(data["sources"]) == 1

    assert data["sources"][0]["title"] == "Hemoglobin Test"
    assert data["sources"][0]["source"] == "MedlinePlus"
    assert (
        data["sources"][0]["source_url"]
        == "https://medlineplus.gov/lab-tests/hemoglobin-test/"
    )

    mock_service.explain_report.assert_awaited_once()

    call_kwargs = (
        mock_service.explain_report.await_args.kwargs
    )

    assert (
        call_kwargs["user_question"]
        == "What does my hemoglobin result mean?"
    )

    report_text = call_kwargs["report_text"]

    assert "Hemoglobin: 13.5 g/dL" in report_text
    assert "White Blood Cell Count: 7200 /uL" in report_text
    assert "Platelets: 250000 /uL" in report_text

@pytest.mark.asyncio
async def test_explain_nonexistent_report(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/reports/507f1f77bcf86cd799439011/explain",
        json={
            "question": "What does my hemoglobin result mean?"
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Report not found."


@pytest.mark.asyncio
async def test_explain_invalid_report_id(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/reports/not-a-valid-id/explain",
        json={
            "question": "What does my hemoglobin result mean?"
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Report not found."


@pytest.mark.asyncio
async def test_explain_report_rejects_empty_question(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/reports/507f1f77bcf86cd799439011/explain",
        json={
            "question": "",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_explain_report_rejects_long_question(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/reports/507f1f77bcf86cd799439011/explain",
        json={
            "question": "a" * 2001,
        },
    )

    assert response.status_code == 422