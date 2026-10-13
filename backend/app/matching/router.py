"""Trial match engine router — REQ-05, REQ-06, REQ-07.

Enhanced with NEW FEATURES:
  - Per-criterion eligibility breakdown (Feature 1)
  - Composite enrollment readiness score (Feature 2)
  - Geographic proximity ranking (Feature 4)
"""

from __future__ import annotations

import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.jwt_handler import get_current_user
from app.eligibility.criterion_engine import evaluate_trial_eligibility
from app.models.schemas import (
    EntityStatus,
    MatchSearchRequest,
    MatchSearchResponse,
    TokenPayload,
    TrialMatch,
)
from app.trials.proximity_service import fetch_trial_locations, rank_by_proximity
from app.trials.qdrant_service import get_qdrant_service
from app.evidence.ledger_service import approved_evidence_spans, link_criterion_evidence
from app.trials.freshness_service import evaluate_trial_freshness

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/match", tags=["Matching"])


def _generate_missing_variables(
    eligibility_criteria: str, approved_terms: list[str]
) -> list[str]:
    """Compare trial eligibility criteria against approved patient entities.

    Identifies eligibility requirements that were NOT found in the
    patient transcript, forming the "Missing Variables" checklist (REQ-06).

    Args:
        eligibility_criteria: Raw eligibility text from the trial.
        approved_terms: Lowercase list of approved entity terms from the visit.

    Returns:
        List of eligibility requirement strings not covered by the transcript.
    """
    if not eligibility_criteria:
        return []

    # Split eligibility into individual criteria lines
    lines = re.split(r"\n|;\s*|\d+\.\s+|(?<=[.!?])\s+", eligibility_criteria)
    missing: list[str] = []

    for line in lines:
        line = line.strip()
        if len(line) < 10:
            continue
        # Skip exclusion criteria sections
        if re.search(r"\bexclusion\b", line, re.IGNORECASE):
            continue
        # Check if any approved term appears in this criterion
        line_lower = line.lower()
        covered = any(term in line_lower for term in approved_terms)
        if not covered:
            missing.append(line[:200])  # truncate very long criteria lines

    return missing[:10]  # cap at 10 missing variables for UI readability


@router.post("/search", response_model=MatchSearchResponse, status_code=status.HTTP_200_OK)
async def search_trials(
    body: MatchSearchRequest,
    clinic_zip: str = Query(default="", description="5-digit clinic ZIP for proximity ranking (NEW)"),
    current_user: TokenPayload = Depends(get_current_user),
) -> MatchSearchResponse:
    """Query Qdrant for trial matches using only APPROVED clinical entities.

    Enhanced with per-criterion eligibility breakdown (Feature 1),
    composite enrollment readiness score (Feature 2), and geographic
    proximity ranking (Feature 4).

    Args:
        body: MatchSearchRequest with approved_entities and session_id.
        clinic_zip: Optional 5-digit ZIP code for proximity ranking.
        current_user: Authenticated user from JWT.

    Returns:
        MatchSearchResponse with enriched trial matches.
    """
    approved_terms = [
        e.term
        for e in body.approved_entities
        if e.status == EntityStatus.APPROVED
        and not e.negated
        and e.context == "patient"
    ]

    if not approved_terms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No approved patient-context entities found. Human verification required.",
        )

    negated_terms = [
        e.term for e in body.approved_entities if e.negated
    ]
    all_terms = [e.term for e in body.approved_entities]

    qdrant = get_qdrant_service()
    try:
        raw_matches = await qdrant.search(approved_terms)
    except Exception as exc:
        logger.error("Qdrant search failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector database search unavailable. Please try again.",
        )

    approved_lower = [t.lower() for t in approved_terms]
    negated_lower = [t.lower() for t in negated_terms]
    all_lower = [t.lower() for t in all_terms]

    trial_matches: list[dict] = []
    approved_spans = approved_evidence_spans(body.approved_entities, body.evidence_spans)

    for m in raw_matches:
        eligibility_text = m.get("eligibility_criteria", "")

        # FEATURE 1 & 2: Per-criterion breakdown + enrollment readiness score
        breakdown = evaluate_trial_eligibility(
            nct_id=m["nct_id"],
            title=m["title"],
            eligibility_text=eligibility_text,
            similarity_score=m["score"],
            approved_terms=approved_lower,
            negated_terms=negated_lower,
            all_terms=all_lower,
        )

        # Classic missing variables for backwards compatibility
        missing = _generate_missing_variables(eligibility_text, approved_lower)

        # FEATURE 4: Fetch location data for proximity ranking
        locations = await fetch_trial_locations(m["nct_id"])

        criterion_breakdown = [
            {
                "criterion_text": r.criterion_text,
                "verdict": r.verdict.value,
                "matched_entity": r.matched_entity,
                "confidence": r.confidence,
                "is_inclusion": r.is_inclusion,
                "explanation": r.explanation,
            }
            for r in breakdown.criteria_results
        ]
        trial_matches.append({
            "nct_id": m["nct_id"],
            "title": m["title"],
            "score": m["score"],
            "phase": m["phase"],
            "status": m["status"],
            "brief_summary": m["brief_summary"],
            "conditions": m["conditions"],
            "sponsor": m["sponsor"],
            "missing_variables": missing,
            "criterion_breakdown": criterion_breakdown,
            "enrollment_readiness_score": breakdown.enrollment_readiness_score,
            "score_explanation": breakdown.score_explanation,
            "locations": locations,
            "criterion_evidence": link_criterion_evidence(criterion_breakdown, approved_spans),
            "freshness": evaluate_trial_freshness(
                status=m["status"],
                last_updated=m.get("last_updated", ""),
                locations=locations,
            ),
        })

    # FEATURE 4: Re-rank by proximity if clinic_zip provided
    if clinic_zip:
        trial_matches = rank_by_proximity(trial_matches, clinic_zip)
    else:
        trial_matches.sort(key=lambda m: -m["enrollment_readiness_score"])

    result_matches = [TrialMatch(**m) for m in trial_matches]

    return MatchSearchResponse(
        matches=result_matches,
        session_id=body.session_id,
        query_entity_count=len(approved_terms),
        match_count=len(result_matches),
    )
