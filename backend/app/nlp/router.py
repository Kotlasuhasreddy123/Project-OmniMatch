"""NLP entity extraction router — REQ-03."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.auth.jwt_handler import get_current_user
from app.models.schemas import (
    ClinicalEntity,
    EntityStatus,
    EntityType,
    NLPExtractRequest,
    NLPExtractResponse,
    TokenPayload,
)
from app.nlp.negex_pipeline import extract_entities

router = APIRouter(prefix="/api/v1/nlp", tags=["NLP"])


@router.post("/extract", response_model=NLPExtractResponse, status_code=status.HTTP_200_OK)
async def extract_clinical_entities(
    body: NLPExtractRequest,
    current_user: TokenPayload = Depends(get_current_user),
) -> NLPExtractResponse:
    """Extract clinical entities from a transcription using the NegEx pipeline.

    Negated and family-context entities are returned but tagged appropriately
    so the Human-in-the-Loop UI can display them for staff review.

    Args:
        body: NLPExtractRequest with transcription text and session_id.
        current_user: Authenticated user from JWT.

    Returns:
        NLPExtractResponse with full entity list and summary counts.
    """
    raw_entities = extract_entities(body.transcription)

    entities: list[ClinicalEntity] = []
    for e in raw_entities:
        entities.append(
            ClinicalEntity(
                term=e["term"],
                entity_type=EntityType(e["entity_type"]),
                negated=e["negated"],
                context=e["context"],
                confidence=e["confidence"],
                status=EntityStatus.PENDING,
            )
        )

    affirmed = sum(
        1 for e in entities if not e.negated and e.context == "patient"
    )
    negated = sum(1 for e in entities if e.negated)
    family = sum(1 for e in entities if e.context == "family")

    return NLPExtractResponse(
        entities=entities,
        session_id=body.session_id,
        affirmed_count=affirmed,
        negated_count=negated,
        family_context_count=family,
    )
