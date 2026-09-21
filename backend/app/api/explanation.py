import logging
from functools import lru_cache

from fastapi import APIRouter, HTTPException, status

from app.schemas.explanation import (
    ExplanationRequest,
    ExplanationResponse,
    ExplanationSource,
)
from app.services.explanation import ExplanationService


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/explanations",
    tags=["Explanations"],
)


@lru_cache(maxsize=1)
def get_explanation_service() -> ExplanationService:
    """Return a reusable explanation service instance."""
    return ExplanationService()


@router.post(
    "",
    response_model=ExplanationResponse,
    status_code=status.HTTP_200_OK,
)
async def create_explanation(
    request: ExplanationRequest,
) -> ExplanationResponse:
    """Generate a grounded medical explanation."""

    try:
        service = get_explanation_service()

        result = await service.explain(
            user_question=request.question,
        )

        # Deduplicate sources while preserving their original order.
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

        return ExplanationResponse(
            answer=result.answer,
            sources=unique_sources,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Failed to generate medical explanation."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate the medical explanation.",
        ) from exc