"""Tests for 7 new differentiating features of OmniMatch.

These test capabilities that NO existing clinical trial matching system
(TrialMatchAI, PRISM, TrialGPT, Nuance DAX, Abridge as of 2025) provides.
"""

from __future__ import annotations

import pytest
from app.eligibility.criterion_engine import (
    CriterionVerdict,
    _split_criteria,
    compute_enrollment_readiness,
    evaluate_trial_eligibility,
)
from app.trials.proximity_service import haversine_distance, rank_by_proximity


# ---------------------------------------------------------------------------
# FEATURE 1: Per-Criterion Eligibility Breakdown
# ---------------------------------------------------------------------------

class TestCriterionEngine:
    """Validate per-criterion verdict classification."""

    def test_met_verdict_when_approved_term_matches(self):
        """MET verdict when approved entity matches inclusion criterion."""
        breakdown = evaluate_trial_eligibility(
            nct_id="NCT00000001",
            title="Test Trial",
            eligibility_text="Inclusion Criteria:\n* Patients with type 2 diabetes",
            similarity_score=0.8,
            approved_terms=["diabetes"],
            negated_terms=[],
            all_terms=["diabetes"],
        )
        met = [r for r in breakdown.criteria_results if r.verdict == CriterionVerdict.MET]
        assert len(met) >= 1
        assert any("diabetes" in r.matched_entity for r in met if r.matched_entity)

    def test_not_met_verdict_for_negated_terms(self):
        """NOT_MET verdict when negated entity matches criterion."""
        breakdown = evaluate_trial_eligibility(
            nct_id="NCT00000002",
            title="Test Trial 2",
            eligibility_text="Inclusion Criteria:\n* Patients with hypertension",
            similarity_score=0.7,
            approved_terms=[],
            negated_terms=["hypertension"],
            all_terms=["hypertension"],
        )
        not_met = [r for r in breakdown.criteria_results if r.verdict == CriterionVerdict.NOT_MET]
        assert len(not_met) >= 1

    def test_unknown_verdict_for_lab_criteria(self):
        """UNKNOWN verdict for criteria requiring lab values (HbA1c, eGFR, etc.)."""
        breakdown = evaluate_trial_eligibility(
            nct_id="NCT00000003",
            title="Test Trial 3",
            eligibility_text="Inclusion Criteria:\n* HbA1c > 7.5%",
            similarity_score=0.75,
            approved_terms=["diabetes"],
            negated_terms=[],
            all_terms=["diabetes"],
        )
        unknown = [r for r in breakdown.criteria_results if r.verdict == CriterionVerdict.UNKNOWN]
        assert len(unknown) >= 1, "Lab value criteria must be tagged UNKNOWN"

    def test_missing_verdict_when_criterion_not_in_transcript(self):
        """MISSING verdict when criterion topic not mentioned in visit."""
        breakdown = evaluate_trial_eligibility(
            nct_id="NCT00000004",
            title="Test Trial 4",
            eligibility_text="Inclusion Criteria:\n* Patients with active rheumatoid arthritis",
            similarity_score=0.65,
            approved_terms=["diabetes"],  # diabetes approved, but no arthritis
            negated_terms=[],
            all_terms=["diabetes"],
        )
        missing = [r for r in breakdown.criteria_results if r.verdict == CriterionVerdict.MISSING]
        assert len(missing) >= 1

    def test_split_criteria_separates_inclusion_exclusion(self):
        """Eligibility text split correctly into inclusion and exclusion lists."""
        text = """
        Inclusion Criteria:
        * Patients with diabetes
        * Age 18-75

        Exclusion Criteria:
        * Active malignancy
        * Severe renal failure
        """
        inclusion, exclusion = _split_criteria(text)
        assert any("diabetes" in c.lower() for c in inclusion), "diabetes should be in inclusion"
        assert any("malignancy" in c.lower() or "renal" in c.lower() for c in exclusion), \
            "malignancy/renal should be in exclusion"


# ---------------------------------------------------------------------------
# FEATURE 2: Composite Enrollment Readiness Score
# ---------------------------------------------------------------------------

class TestEnrollmentReadinessScore:
    """Validate the 0–100 composite enrollment readiness score."""

    def test_high_score_for_all_met_criteria(self):
        """Score should be high when all inclusion criteria are met."""
        from app.eligibility.criterion_engine import CriterionResult
        inc = [
            CriterionResult("diabetes", CriterionVerdict.MET, "diabetes", 0.9, True, ""),
            CriterionResult("hypertension", CriterionVerdict.MET, "hypertension", 0.85, True, ""),
        ]
        exc = []
        score, _ = compute_enrollment_readiness(inc, exc, similarity_score=0.9)
        assert score >= 70, f"Expected high score, got {score}"

    def test_low_score_for_all_missing_criteria(self):
        """Score should be low when all inclusion criteria are missing."""
        from app.eligibility.criterion_engine import CriterionResult
        inc = [
            CriterionResult("diabetes", CriterionVerdict.MISSING, None, 0.0, True, ""),
            CriterionResult("hypertension", CriterionVerdict.MISSING, None, 0.0, True, ""),
        ]
        exc = []
        score, _ = compute_enrollment_readiness(inc, exc, similarity_score=0.5)
        assert score < 50, f"Expected low score, got {score}"

    def test_score_penalized_for_exclusion_violations(self):
        """Score should decrease when patient has exclusion criteria."""
        from app.eligibility.criterion_engine import CriterionResult
        inc = [CriterionResult("diabetes", CriterionVerdict.MET, "diabetes", 0.9, True, "")]
        exc = [CriterionResult("renal failure", CriterionVerdict.MET, "kidney", 0.8, False, "")]
        score_with_violation, _ = compute_enrollment_readiness(inc, exc, 0.85)

        exc_none = []
        score_without, _ = compute_enrollment_readiness(inc, exc_none, 0.85)

        assert score_with_violation < score_without, \
            "Exclusion criterion violation should reduce score"

    def test_score_always_0_to_100(self):
        """Score must always be in [0, 100] range."""
        from app.eligibility.criterion_engine import CriterionResult
        inc = [CriterionResult("x", CriterionVerdict.MISSING, None, 0, True, "")]
        exc = [
            CriterionResult("y", CriterionVerdict.MET, "y", 0.9, False, ""),
            CriterionResult("z", CriterionVerdict.MET, "z", 0.9, False, ""),
            CriterionResult("w", CriterionVerdict.MET, "w", 0.9, False, ""),
            CriterionResult("v", CriterionVerdict.MET, "v", 0.9, False, ""),
        ]
        score, _ = compute_enrollment_readiness(inc, exc, 0.0)
        assert 0.0 <= score <= 100.0


# ---------------------------------------------------------------------------
# FEATURE 4: Geographic Proximity Ranking
# ---------------------------------------------------------------------------

class TestProximityRanking:
    """Validate geographic proximity calculation and ranking."""

    def test_haversine_nyc_to_chicago(self):
        """NYC to Chicago should be approximately 711 air miles."""
        dist = haversine_distance(40.7484, -73.9967, 41.8827, -87.6233)
        assert 690 < dist < 730, f"Expected ~711mi, got {dist:.1f}mi"

    def test_haversine_same_point_is_zero(self):
        """Distance from a point to itself is 0."""
        dist = haversine_distance(40.0, -74.0, 40.0, -74.0)
        assert dist < 0.01

    def test_rank_by_proximity_puts_nearby_first(self):
        """Nearby trials should appear before distant ones."""
        matches = [
            {
                "nct_id": "NCT_FAR",
                "enrollment_readiness_score": 80,
                "score": 0.8,
                "locations": [{"zip": "90001", "city": "Los Angeles", "state": "CA"}],
            },
            {
                "nct_id": "NCT_CLOSE",
                "enrollment_readiness_score": 70,
                "score": 0.7,
                "locations": [{"zip": "10001", "city": "New York", "state": "NY"}],
            },
        ]
        # Clinic ZIP is in New York area
        ranked = rank_by_proximity(matches, clinic_zip="10001", max_distance_miles=500)
        assert len(ranked) >= 1

        # Close trial (NY) should be in the "within" group
        close_idx = next(
            (i for i, m in enumerate(ranked) if m["nct_id"] == "NCT_CLOSE"), None
        )
        far_idx = next(
            (i for i, m in enumerate(ranked) if m["nct_id"] == "NCT_FAR"), None
        )
        if close_idx is not None and far_idx is not None:
            assert close_idx < far_idx, "Nearby trial should rank higher than distant one"

    def test_rank_by_proximity_handles_unknown_zip(self):
        """Unknown clinic ZIP should not crash — returns unranked list."""
        matches = [
            {"nct_id": "NCT_X", "enrollment_readiness_score": 75, "score": 0.75, "locations": []},
        ]
        ranked = rank_by_proximity(matches, clinic_zip="99999")
        assert len(ranked) == 1
        assert ranked[0]["nearest_site_miles"] is None


# ---------------------------------------------------------------------------
# FEATURE 3: Longitudinal Timeline (unit tests for service layer)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upsert_and_retrieve_patient_timeline(tmp_db_path: str):
    """Entities from multiple sessions accumulate in patient timeline."""
    from app import config as cfg
    cfg.settings.sqlite_db_path = tmp_db_path
    import app.models.database as db_mod
    db_mod.DB_PATH = tmp_db_path

    from app.timeline.timeline_service import (
        ensure_timeline_table,
        upsert_patient_entities,
        get_patient_timeline,
        get_cumulative_entities,
    )

    await ensure_timeline_table()

    # Session 1: diabetes + hypertension
    await upsert_patient_entities(
        "patient-001", "sess-001",
        [
            {"term": "diabetes", "entity_type": "DISEASE", "confidence": 0.9},
            {"term": "hypertension", "entity_type": "DISEASE", "confidence": 0.85},
        ],
    )

    # Session 2: diabetes again (should increment mention_count) + new entity
    await upsert_patient_entities(
        "patient-001", "sess-002",
        [
            {"term": "diabetes", "entity_type": "DISEASE", "confidence": 0.92},
            {"term": "metformin", "entity_type": "MEDICATION", "confidence": 0.88},
        ],
    )

    timeline = await get_patient_timeline("patient-001")
    assert len(timeline) == 3, f"Expected 3 unique entities, got {len(timeline)}"

    # Diabetes should have mention_count = 2
    diabetes_entry = next((e for e in timeline if e["entity_term"] == "diabetes"), None)
    assert diabetes_entry is not None
    assert diabetes_entry["mention_count"] == 2, "Diabetes mentioned in 2 sessions"

    # Cumulative entities should include all 3
    cumulative = await get_cumulative_entities("patient-001")
    assert "diabetes" in cumulative
    assert "hypertension" in cumulative
    assert "metformin" in cumulative


@pytest.mark.asyncio
async def test_eligibility_unlock_detection(tmp_db_path: str):
    """New session entities should unlock previously-missing trial criteria."""
    from app import config as cfg
    cfg.settings.sqlite_db_path = tmp_db_path

    from app.timeline.timeline_service import detect_eligibility_unlocks

    # Previous session: diabetes matched NCT_X, but hypertension was missing
    previous_missing = {
        "NCT_X": ["Patients must have hypertension", "Age 18-75"],
    }
    new_terms = ["hypertension", "fatigue"]

    unlocks = await detect_eligibility_unlocks(
        patient_pseudo="patient-002",
        new_session_terms=new_terms,
        previous_missing_variables=previous_missing,
    )

    assert len(unlocks) >= 1, "Should detect hypertension unlocking NCT_X criterion"
    assert any(u["nct_id"] == "NCT_X" for u in unlocks)
    assert any("hypertension" in u["entity_term"] for u in unlocks)


# ---------------------------------------------------------------------------
# FEATURE 6: Transcript Confidence (schema validation)
# ---------------------------------------------------------------------------

def test_transcription_response_includes_word_confidences():
    """TranscriptionResponse schema must include word_confidences field."""
    from app.models.schemas import TranscriptionResponse
    from datetime import datetime

    resp = TranscriptionResponse(
        transcription="Patient has diabetes.",
        duration_seconds=1.5,
        language="en",
        session_id="sess-test",
        word_confidences=[
            {"word": "Patient", "confidence": 0.95, "start_time": 0.0},
            {"word": "has", "confidence": 0.99, "start_time": 0.3},
            {"word": "diabetes", "confidence": 0.62, "start_time": 0.6},  # low confidence
        ],
    )
    assert len(resp.word_confidences) == 3
    low_conf = [w for w in resp.word_confidences if w["confidence"] < 0.7]
    assert len(low_conf) == 1  # "diabetes" is flagged
    assert low_conf[0]["word"] == "diabetes"


# ---------------------------------------------------------------------------
# FEATURE 5: Referral schema validation
# ---------------------------------------------------------------------------

def test_referral_request_schema():
    """ReferralRequest must accept required fields without errors."""
    from app.models.schemas import ReferralRequest
    req = ReferralRequest(
        inbox_item_id="inbox-001",
        nct_id="NCT00000001",
        session_id="sess-001",
        trial_title="Diabetes Treatment Study",
        met_criteria=["Patients with type 2 diabetes"],
        patient_pseudo="REDACTED",
    )
    assert req.nct_id == "NCT00000001"
    assert req.patient_pseudo == "REDACTED"
    assert len(req.met_criteria) == 1
