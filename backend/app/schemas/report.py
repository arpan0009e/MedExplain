from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    """Request schema for creating a medical report record."""

    filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Original filename of the uploaded report.",
    )


class ReportResponse(BaseModel):
    """Response schema for a medical report."""

    report_id: str
    filename: str
    status: str