import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_report(
    client: AsyncClient,
) -> None:
    """Creating a report should return HTTP 201."""

    response = await client.post(
        "/api/v1/reports",
        json={
            "filename": "test_report.pdf",
        },
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
    """A created report should be retrievable by ID."""

    create_response = await client.post(
        "/api/v1/reports",
        json={
            "filename": "retrieval_test.pdf",
        },
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
    """Requesting a nonexistent report should return 404."""

    response = await client.get(
        "/api/v1/reports/507f1f77bcf86cd799439011"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Report not found."


@pytest.mark.asyncio
async def test_get_invalid_report_id(
    client: AsyncClient,
) -> None:
    """An invalid MongoDB ObjectId should return 404."""

    response = await client.get(
        "/api/v1/reports/not-a-valid-id"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Report not found."