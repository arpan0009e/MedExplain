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
    """Response schema for a basic medical report record."""

    report_id: str
    filename: str
    status: str


class ReportDetailResponse(BaseModel):
    """Response schema for a stored and processed medical report."""

    report_id: str
    filename: str
    status: str
    page_count: int
    text: str


class ReportUploadResponse(BaseModel):
    """Response schema for a processed PDF medical report."""

    report_id: str
    filename: str
    page_count: int
    text: str