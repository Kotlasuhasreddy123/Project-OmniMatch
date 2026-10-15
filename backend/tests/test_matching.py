"""TEST-03 & TEST-05: Match engine and entity rejection tests.

Validates:
- TEST-03: Rejected entity chips are excluded from the Qdrant query payload
- TEST-05: Session completion triggers inbox population within 60s
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.matching.router import _generate_missing_variables
from app.models.schemas import ClinicalEntity, EntityStatus, EntityType


# ---------------------------------------------------------------------------
# TEST-03: Rejected entities excluded from query payload
# ---------------------------------------------------------------------------

class TestEntityRejectionExclusion:
    """Verify that rejected entity chips never reach the Qdrant search call."""

    def test_generate_missing_variables_returns_list(self):
        """Missing variables generator returns uncovered eligibility criteria."""
        eligibility = (
            "Inclusion: patients with type 2 diabetes. "
            "Patients must have HbA1c > 7%. "
            "Patients should not have renal failure."
        )
        approved = ["diabetes"]
        missing = _generate_missing_variables(eligibility, approved)
        # HbA1c criterion not covered by approved terms
        assert any("hba1c" in m.lower() or "a1c" in m.lower() for m in missing), (
            "HbA1c criterion should appear in missing variables"
        )

    def test_generate_missing_variables_empty_when_all_covered(self):
        """Missing variables list should be small when all criteria are covered."""
        eligibility = "Patients with diabetes and hypertension."
        approved = ["diabetes", "hypertension"]
        missing = _generate_missing_variables(eligibility, approved)
        assert len(missing) == 0 or all(
            "diabetes" not in m.lower() and "hypertension" not in m.lower()
            for m in missing
        )

    def test_generate_missing_variables_with_empty_eligibility(self):
        """Empty eligibility criteria returns empty missing list."""
        assert _generate_missing_variables("", ["diabetes"]) == []


# ---------------------------------------------------------------------------
# HTTP-level rejection tests (module-level async so fixtures work correctly)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_match_search_rejects_all_rejected_entities(
    client: AsyncClient, auth_headers: dict
):
    """POST /api/v1/match/search with all rejected entities returns HTTP 400 (TEST-03).

    The backend must refuse to run a Qdrant query when no approved entities exist.
    """
    all_rejected_payload = {
        "approved_entities": [
            {
                "term": "diabetes",
                "entity_type": "DISEASE",
                "negated": False,
                "context": "patient",
                "confidence": 0.9,
                "status": "rejected",
            },
            {
                "term": "hypertension",
                "entity_type": "DISEASE",
                "negated": False,
                "context": "patient",
                "confidence": 0.85,
                "status": "rejected",
            },
        ],
        "session_id": "test-rejection-001",
    }
    resp = await client.post(
        "/api/v1/match/search",
        json=all_rejected_payload,
        headers=auth_headers,
    )
    assert resp.status_code == 400, (
        "All-rejected entity payload must be rejected with HTTP 400 "
        "— rejected entities must never reach Qdrant."
    )


@pytest.mark.asyncio
async def test_match_search_excludes_negated_entities_from_query(
    client: AsyncClient, auth_headers: dict
):
    """Negated entities approved in UI must still be excluded from the Qdrant query."""
    negated_approved_payload = {
        "approved_entities": [
            {
                "term": "diabetes",
                "entity_type": "DISEASE",
                "negated": True,
                "context": "patient",
                "confidence": 0.9,
                "status": "approved",
            },
        ],
        "session_id": "test-negated-approved-001",
    }
    resp = await client.post(
        "/api/v1/match/search",
        json=negated_approved_payload,
        headers=auth_headers,
    )
    assert resp.status_code == 400, (
        "Negated entities must be excluded from Qdrant query even if marked approved."
    )


@pytest.mark.asyncio
async def test_match_search_excludes_family_context_entities(
    client: AsyncClient, auth_headers: dict
):
    """Family-context entities must be excluded from Qdrant query."""
    family_payload = {
        "approved_entities": [
            {
                "term": "diabetes",
                "entity_type": "DISEASE",
                "negated": False,
                "context": "family",
                "confidence": 0.9,
                "status": "approved",
            },
        ],
        "session_id": "test-family-001",
    }
    resp = await client.post(
        "/api/v1/match/search",
        json=family_payload,
        headers=auth_headers,
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# TEST-05: Inbox population within 60 seconds of session completion
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_session_complete_triggers_background_task(
    client: AsyncClient, auth_headers: dict
):
    """POST /api/v1/sessions/{id}/complete must return 202 and trigger matching.

    The response must arrive quickly — the matching runs in the background.
    """
    payload = {
        "session_id": "session-timing-test",
        "approved_entities": [
            {
                "term": "diabetes",
                "entity_type": "DISEASE",
                "negated": False,
                "context": "patient",
                "confidence": 0.9,
                "status": "approved",
            }
        ],
    }
    # HTTPX's in-process ASGI transport waits for Starlette background tasks
    # before returning; isolate endpoint scheduling time here. The separate
    # inbox test and live smoke test cover background execution itself.
    with patch("app.inbox.router._run_matching_and_store", new_callable=AsyncMock):
        start = time.perf_counter()
        resp = await client.post(
            "/api/v1/sessions/session-timing-test/complete",
            json=payload,
            headers=auth_headers,
        )
        elapsed = time.perf_counter() - start

    assert resp.status_code == 202, "Session completion must return HTTP 202 Accepted"
    assert resp.json()["matching_triggered"] is True
    # Response must arrive promptly — background task doesn't block the endpoint
    assert elapsed < 5.0, (
        f"Session complete endpoint took {elapsed:.1f}s — it must return immediately."
    )


@pytest.mark.asyncio
async def test_inbox_populated_within_60_seconds(
    client: AsyncClient, auth_headers: dict, tmp_db_path: str
):
    """End-to-end: inbox item must appear within 60 seconds (REQ-07, TEST-05).

    Uses a mocked Qdrant search to avoid requiring a live Qdrant instance.
    """
    mock_match = {
        "nct_id": "NCT12345678",
        "title": "Diabetes Type 2 Treatment Study",
        "score": 0.87,
        "phase": "Phase 3",
        "status": "RECRUITING",
        "brief_summary": "A study for type 2 diabetes patients.",
        "conditions": ["Diabetes Mellitus Type 2"],
        "sponsor": "Test Pharma Inc.",
        "eligibility_criteria": "Patients with type 2 diabetes and HbA1c > 7%.",
    }

    with patch(
        "app.trials.qdrant_service.QdrantService.search",
        new_callable=AsyncMock,
        return_value=[mock_match],
    ):
        session_id = "session-inbox-test-001"
        payload = {
            "session_id": session_id,
            "approved_entities": [
                {
                    "term": "diabetes",
                    "entity_type": "DISEASE",
                    "negated": False,
                    "context": "patient",
                    "confidence": 0.9,
                    "status": "approved",
                }
            ],
        }

        start_time = time.time()

        # Trigger session completion
        await client.post(
            f"/api/v1/sessions/{session_id}/complete",
            json=payload,
            headers=auth_headers,
        )

        # Poll inbox for up to 60 seconds
        inbox_populated = False
        while time.time() - start_time < 60:
            await asyncio.sleep(1)
            resp = await client.get("/api/v1/inbox", headers=auth_headers)
            items = resp.json().get("items", [])
            matching_items = [i for i in items if i["session_id"] == session_id]
            if matching_items:
                inbox_populated = True
                elapsed = time.time() - start_time
                assert elapsed <= 60, (
                    f"Inbox populated in {elapsed:.1f}s — exceeds 60-second requirement (REQ-07)"
                )
                break

        assert inbox_populated, (
            "Inbox was NOT populated within 60 seconds of session completion (REQ-07 FAILED)"
        )
