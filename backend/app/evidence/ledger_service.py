"""Evidence Ledger helpers.

This module provides Abridge-style linked evidence without persisting raw
audio, transcription text, or protected identifiers.  A reviewer can verify
the current browser transcript while the backend retains only stable hashes,
offsets, approval state, and a tamper-evident event hash.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone

import aiosqlite

from app.config import settings
from app.models.schemas import (
    ClinicalEntity,
    CriterionEvidence,
    EvidenceLedgerRequest,
    EvidenceLedgerResponse,
    EvidenceSpan,
    EntityStatus,
)


def _canonical_event(session_id: str, entries: list[dict]) -> str:
    """Generate a deterministic digest for the PHI-minimized evidence event."""
    payload = json.dumps(
        {"session_id": session_id, "entries": entries},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def approved_evidence_spans(
    entities: list[ClinicalEntity], spans: list[EvidenceSpan]
) -> list[EvidenceSpan]:
    """Return only spans for approved, patient-context, non-negated entities."""
    approved_terms = {
        entity.term.strip().casefold()
        for entity in entities
        if entity.status == EntityStatus.APPROVED
        and not entity.negated
        and entity.context == "patient"
    }
    return [span for span in spans if span.entity_term.strip().casefold() in approved_terms]


def link_criterion_evidence(
    criterion_breakdown: list[dict], spans: list[EvidenceSpan]
) -> list[CriterionEvidence]:
    """Attach approved transcript anchors only to MET criterion results."""
    by_term = {span.entity_term.strip().casefold(): span for span in spans}
    evidence: list[CriterionEvidence] = []
    for criterion in criterion_breakdown:
        if criterion.get("verdict") != "MET":
            continue
        term = (criterion.get("matched_entity") or "").strip().casefold()
        span = by_term.get(term)
        if not span:
            continue
        evidence.append(
            CriterionEvidence(
                criterion_text=criterion.get("criterion_text", ""),
                entity_term=span.entity_term,
                excerpt_sha256=span.excerpt_sha256,
                start_char=span.start_char,
                end_char=span.end_char,
                human_verified=span.human_verified,
            )
        )
    return evidence


async def record_evidence_ledger(request: EvidenceLedgerRequest) -> EvidenceLedgerResponse:
    """Persist a PHI-minimized, tamper-evident evidence-review event."""
    spans = approved_evidence_spans(request.approved_entities, request.evidence_spans)
    entries = [
        {
            "entity_term": span.entity_term.casefold(),
            "start_char": span.start_char,
            "end_char": span.end_char,
            "excerpt_sha256": span.excerpt_sha256,
            "confidence": span.confidence,
            "human_verified": span.human_verified,
        }
        for span in spans
    ]
    event_hash = _canonical_event(request.session_id, entries)
    ledger_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc)
    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        await db.execute(
            """INSERT INTO evidence_ledger (id, session_id, event_hash, payload_json, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (ledger_id, request.session_id, event_hash, json.dumps(entries), created_at.isoformat()),
        )
        await db.commit()
    return EvidenceLedgerResponse(
        ledger_id=ledger_id,
        session_id=request.session_id,
        verified_entity_count=len(entries),
        event_hash=event_hash,
        created_at=created_at,
    )
