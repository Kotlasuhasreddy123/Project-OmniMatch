"""Tests for the evidence ledger and trial freshness gate renewal features."""

from __future__ import annotations

from datetime import date

import pytest

from app.evidence.ledger_service import approved_evidence_spans, link_criterion_evidence
from app.models.schemas import ClinicalEntity, EntityStatus, EntityType, EvidenceSpan
from app.trials.freshness_service import evaluate_trial_freshness


def _entity(term: str, status: EntityStatus = EntityStatus.APPROVED) -> ClinicalEntity:
    return ClinicalEntity(
        term=term,
        entity_type=EntityType.DISEASE,
        confidence=0.9,
        status=status,
    )


def test_evidence_ledger_uses_only_approved_patient_entities() -> None:
    entities = [_entity("diabetes"), _entity("hypertension", EntityStatus.REJECTED)]
    spans = [
        EvidenceSpan(entity_term="diabetes", start_char=4, end_char=12, excerpt_sha256="a" * 64, confidence=0.92),
        EvidenceSpan(entity_term="hypertension", start_char=20, end_char=32, excerpt_sha256="b" * 64, confidence=0.91),
    ]
    kept = approved_evidence_spans(entities, spans)
    assert [span.entity_term for span in kept] == ["diabetes"]


def test_evidence_links_only_met_criterion_to_hashed_anchor() -> None:
    span = EvidenceSpan(entity_term="diabetes", start_char=4, end_char=12, excerpt_sha256="a" * 64, confidence=0.92)
    evidence = link_criterion_evidence(
        [
            {"criterion_text": "Type 2 diabetes", "verdict": "MET", "matched_entity": "diabetes"},
            {"criterion_text": "HbA1c at least 7", "verdict": "UNKNOWN", "matched_entity": None},
        ],
        [span],
    )
    assert len(evidence) == 1
    assert evidence[0].excerpt_sha256 == "a" * 64


@pytest.mark.parametrize(
    ("status", "last_updated", "locations", "expected"),
    [
        ("RECRUITING", "2026-10-01", [{"city": "Chicago"}], "READY"),
        ("RECRUITING", "2026-06-01", [{"city": "Chicago"}], "REVIEW"),
        ("COMPLETED", "2026-10-01", [{"city": "Chicago"}], "BLOCKED"),
        ("RECRUITING", "2026-10-01", [], "REVIEW"),
    ],
)
def test_trial_freshness_gate(status: str, last_updated: str, locations: list[dict], expected: str) -> None:
    result = evaluate_trial_freshness(
        status=status,
        last_updated=last_updated,
        locations=locations,
        today=date(2026, 10, 10),
    )
    assert result["level"] == expected
