from pydantic import BaseModel, Field


class ExplanationRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Medical question the user wants explained.",
    )


class ExplanationSource(BaseModel):
    title: str
    source: str
    source_url: str


class ExplanationResponse(BaseModel):
    answer: str
    sources: list[ExplanationSource]


class ReportExplanationRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Question about the uploaded medical report.",
    )


class ReportExplanationResponse(BaseModel):
    report_id: str
    answer: str
    sources: list[ExplanationSource]