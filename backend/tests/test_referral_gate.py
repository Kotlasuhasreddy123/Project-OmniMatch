"""A synthetic or stale match must not initiate an outbound referral."""

import json
from datetime import datetime, timezone

import aiosqlite
import pytest


@pytest.mark.asyncio
async def test_simulated_trial_cannot_be_referred(client, auth_headers, tmp_db_path):
    match = {
        "nct_id": "DEMO-T2D-001",
        "freshness": {"recommended_action": "DO_NOT_ROUTE"},
    }
    async with aiosqlite.connect(tmp_db_path) as db:
        await db.execute(
            "INSERT INTO inbox_items (id, session_id, created_at, status, matches_json, approved_entities) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            ("item-1", "session-1", datetime.now(timezone.utc).isoformat(),
             "unread", json.dumps([match]), "[]"),
        )
        await db.commit()

    response = await client.post(
        "/api/v1/referrals",
        headers=auth_headers,
        json={
            "inbox_item_id": "item-1",
            "nct_id": "DEMO-T2D-001",
            "session_id": "session-1",
            "trial_title": "Synthetic study",
            "met_criteria": [],
            "patient_pseudo": "SYNTHETIC",
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_referral_requires_matching_inbox_item(client, auth_headers):
    response = await client.post(
        "/api/v1/referrals",
        headers=auth_headers,
        json={
            "inbox_item_id": "missing-item",
            "nct_id": "NCT00000001",
            "session_id": "session-1",
            "trial_title": "Unverified study",
            "met_criteria": [],
            "patient_pseudo": "SYNTHETIC",
        },
    )
    assert response.status_code == 404
