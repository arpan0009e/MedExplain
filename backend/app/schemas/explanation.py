from pydantic import BaseModel, Field


class ExplanationRequest(BaseModel):
    """Request body for generating a medical explanation."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Medical question the user wants explained.",
    )


class ExplanationSource(BaseModel):
    """Source used to ground the generated explanation."""

    title: str
    source: str
    source_url: str


class ExplanationResponse(BaseModel):
    """Response returned by the explanation API."""

    answer: str
    sources: list[ExplanationSource]