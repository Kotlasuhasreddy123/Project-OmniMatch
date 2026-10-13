"""Shared Pydantic v2 schemas used across the OmniMatch API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    CLINICAL_STAFF = "CLINICAL_STAFF"


class ConsentAction(str, Enum):
    GRANTED = "CONSENT_GRANTED"
    REVOKED = "CONSENT_REVOKED"


class EntityType(str, Enum):
    DISEASE = "DISEASE"
    SYMPTOM = "SYMPTOM"
    MEDICATION = "MEDICATION"
    PROCEDURE = "PROCEDURE"
    LAB_VALUE = "LAB_VALUE"


class EntityStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class InboxStatus(str, Enum):
    UNREAD = "unread"
    REVIEWED = "reviewed"


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int


class TokenPayload(BaseModel):
    sub: str          # username
    role: UserRole
    exp: int


# ---------------------------------------------------------------------------
# Consent
# ---------------------------------------------------------------------------

class ConsentRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128)
    action: ConsentAction
    patient_pseudonym: str = Field(
        default="REDACTED",
        description="Pseudonymized patient identifier — no real PHI",
        max_length=64,
    )


class ConsentResponse(BaseModel):
    logged: bool
    audit_id: str
    timestamp: datetime


# ---------------------------------------------------------------------------
# Transcription
# ---------------------------------------------------------------------------

class TranscriptionResponse(BaseModel):
    transcription: str
    duration_seconds: float
    language: str
    session_id: str
    # NEW FEATURE 6: Word-level confidence for heatmap display
    word_confidences: list[dict] = Field(
        default_factory=list,
        description="List of {word, confidence, start_time} for transcript heatmap. "
                    "Words with confidence < 0.7 are highlighted amber in the UI.",
    )


# ---------------------------------------------------------------------------
# NLP Entities
# ---------------------------------------------------------------------------

class ClinicalEntity(BaseModel):
    term: str
    entity_type: EntityType
    negated: bool = False
    context: Literal["patient", "family", "hypothetical"] = "patient"
    confidence: float = Field(..., ge=0.0, le=1.0)
    status: EntityStatus = EntityStatus.PENDING


# ---------------------------------------------------------------------------
# Renewed Feature 8: Evidence Ledger
# ---------------------------------------------------------------------------

class EvidenceSpan(BaseModel):
    """A client-side transcript anchor for a human-verified entity.

    The API accepts only a SHA-256 digest and character offsets.  Raw audio and
    transcript quotations are deliberately not persisted in the ledger.
    """

    entity_term: str = Field(..., min_length=1, max_length=256)
    start_char: int = Field(..., ge=0)
    end_char: int = Field(..., gt=0)
    excerpt_sha256: str = Field(..., min_length=64, max_length=64)
    confidence: float = Field(..., ge=0.0, le=1.0)
    human_verified: bool = True


class CriterionEvidence(BaseModel):
    """An auditable, PHI-minimizing link from a criterion to approved evidence."""

    criterion_text: str
    entity_term: str
    excerpt_sha256: str
    start_char: int
    end_char: int
    human_verified: bool


class EvidenceLedgerRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128)
    approved_entities: list[ClinicalEntity]
    evidence_spans: list[EvidenceSpan] = Field(default_factory=list)


class EvidenceLedgerResponse(BaseModel):
    ledger_id: str
    session_id: str
    verified_entity_count: int
    event_hash: str
    created_at: datetime


class NLPExtractRequest(BaseModel):
    transcription: str = Field(..., min_length=1, max_length=50_000)
    session_id: str


class NLPExtractResponse(BaseModel):
    entities: list[ClinicalEntity]
    session_id: str
    affirmed_count: int
    negated_count: int
    family_context_count: int


# ---------------------------------------------------------------------------
# Trial Matching
# ---------------------------------------------------------------------------

class MatchSearchRequest(BaseModel):
    approved_entities: list[ClinicalEntity]
    session_id: str
    evidence_spans: list[EvidenceSpan] = Field(default_factory=list)
    # Validation of approved vs rejected status is handled in the route handler,
    # not here, so the router can return HTTP 400 (not 422) with a clear message.


class TrialMatch(BaseModel):
    nct_id: str
    title: str
    score: float = Field(..., ge=0.0, le=1.0)
    phase: str
    status: str
    brief_summary: str
    conditions: list[str]
    sponsor: str
    missing_variables: list[str]
    # NEW FEATURE 1: Per-criterion eligibility breakdown
    criterion_breakdown: list[dict] = Field(
        default_factory=list,
        description="Per-criterion verdict: MET | NOT_MET | MISSING | UNKNOWN",
    )
    # NEW FEATURE 2: Composite enrollment readiness score
    enrollment_readiness_score: float = Field(
        default=0.0,
        description="Composite 0–100 score combining similarity + inclusion rate − exclusion penalty",
    )
    score_explanation: str = ""
    # NEW FEATURE 4: Geographic proximity
    nearest_site_miles: float | None = None
    nearest_site_city: str = ""
    locations: list[dict] = Field(default_factory=list)
    # Renewed Feature 8: criterion-to-transcript evidence links.  These only
    # reference approved, hashed spans; the backend never stores audio.
    criterion_evidence: list[CriterionEvidence] = Field(default_factory=list)
    # Renewed Feature 9: freshness gate prevents a similarity result from
    # appearing ready for outreach when registry/site status is uncertain.
    freshness: dict = Field(default_factory=dict)


class MatchSearchResponse(BaseModel):
    matches: list[TrialMatch]
    session_id: str
    query_entity_count: int
    match_count: int


# ---------------------------------------------------------------------------
# Inbox
# ---------------------------------------------------------------------------

class InboxItem(BaseModel):
    id: str
    session_id: str
    created_at: datetime
    status: InboxStatus = InboxStatus.UNREAD
    matches: list[TrialMatch]
    approved_entities: list[str]    # terms only, for display


class InboxListResponse(BaseModel):
    items: list[InboxItem]
    total: int
    unread_count: int


# ---------------------------------------------------------------------------
# Trials Sync
# ---------------------------------------------------------------------------

class SyncResponse(BaseModel):
    synced_count: int
    duration_seconds: float
    timestamp: datetime
    status: Literal["success", "partial", "failed"]


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

class SessionCompleteRequest(BaseModel):
    session_id: str
    approved_entities: list[ClinicalEntity]
    evidence_spans: list[EvidenceSpan] = Field(default_factory=list)


class SessionCompleteResponse(BaseModel):
    session_id: str
    matching_triggered: bool
    message: str


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    qdrant_connected: bool
    whisper_loaded: bool
    version: str = "1.0.0"


# ---------------------------------------------------------------------------
# NEW FEATURE 5: Referral
# ---------------------------------------------------------------------------

class ReferralRequest(BaseModel):
    inbox_item_id: str
    nct_id: str
    session_id: str
    patient_pseudo: str = "REDACTED"
    trial_title: str
    met_criteria: list[str] = Field(default_factory=list)
    webhook_url: str | None = None


class ReferralResponse(BaseModel):
    referral_id: str
    status: str
    webhook_fired: bool


# ---------------------------------------------------------------------------
# NEW FEATURE 3: Timeline
# ---------------------------------------------------------------------------

class TimelineEntry(BaseModel):
    entity_term: str
    entity_type: str
    confidence: float
    first_seen: datetime
    last_seen: datetime
    mention_count: int
    session_id: str


class PatientTimelineResponse(BaseModel):
    patient_pseudo: str
    entries: list[TimelineEntry]
    total_entities: int
    unlock_events: list[dict] = Field(default_factory=list)
