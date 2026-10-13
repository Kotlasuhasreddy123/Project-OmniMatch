#!/usr/bin/env python3
"""
seed_trials.py — Seed the Qdrant vector database with real ClinicalTrials.gov data.

This script fetches RECRUITING trials across multiple conditions relevant to
OmniMatch's target use cases (diabetes, hypertension, cancer, COPD, etc.)
and indexes them into Qdrant for vector similarity matching.

Usage:
    cd backend
    python scripts/seed_trials.py [--conditions diabetes hypertension] [--max 500]

Requires:
    - Qdrant running on localhost:6333 (docker run -p 6333:6333 qdrant/qdrant)
    - sentence-transformers installed (pip install sentence-transformers)
    - qdrant-client installed
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import os

# Add backend app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Default conditions to seed — covers major disease areas
DEFAULT_CONDITIONS = [
    "diabetes",
    "hypertension",
    "cancer",
    "copd",
    "heart failure",
    "depression",
    "alzheimer",
    "multiple sclerosis",
    "rheumatoid arthritis",
    "kidney disease",
    "obesity",
    "stroke",
    "parkinson",
    "asthma",
    "atrial fibrillation",
]


async def seed_for_condition(condition: str, max_per_condition: int = 100) -> int:
    """Fetch and index trials for one condition.

    Args:
        condition: Disease/condition search term.
        max_per_condition: Maximum trials to fetch per condition.

    Returns:
        Number of trials indexed.
    """
    import httpx
    from app.trials.qdrant_service import get_qdrant_service

    qdrant = get_qdrant_service()
    await qdrant.ensure_collection()

    base_url = "https://clinicaltrials.gov/api/v2/studies"
    fields = [
        "NCTId", "BriefTitle", "OverallStatus", "Phase",
        "Condition", "BriefSummary", "EligibilityCriteria",
        "LeadSponsorName", "LastUpdatePostDate",
        "LocationCountry", "LocationCity", "LocationState", "LocationZip",
    ]

    indexed = 0
    next_page_token = None

    async with httpx.AsyncClient(timeout=30.0) as client:
        while indexed < max_per_condition:
            params = {
                "format": "json",
                "pageSize": min(50, max_per_condition - indexed),
                "fields": "|".join(fields),
                "filter.overallStatus": "RECRUITING",
                "query.cond": condition,
            }
            if next_page_token:
                params["pageToken"] = next_page_token

            try:
                resp = await client.get(base_url, params=params)
                resp.raise_for_status()
            except httpx.HTTPError as e:
                logger.warning("API error for '%s': %s", condition, e)
                break

            data = resp.json()
            studies = data.get("studies", [])
            if not studies:
                break

            for study in studies:
                proto = study.get("protocolSection", {})
                id_mod = proto.get("identificationModule", {})
                status_mod = proto.get("statusModule", {})
                desc_mod = proto.get("descriptionModule", {})
                elig_mod = proto.get("eligibilityModule", {})
                cond_mod = proto.get("conditionsModule", {})
                spon_mod = proto.get("sponsorCollaboratorsModule", {})
                design_mod = proto.get("designModule", {})
                loc_mod = proto.get("contactsLocationsModule", {})

                phases = design_mod.get("phases", [])
                locations = [
                    {
                        "facility": loc.get("facility", ""),
                        "city": loc.get("city", ""),
                        "state": loc.get("state", ""),
                        "country": loc.get("country", ""),
                        "zip": loc.get("zip", ""),
                    }
                    for loc in loc_mod.get("locations", [])
                ]

                trial = {
                    "nct_id": id_mod.get("nctId", ""),
                    "title": id_mod.get("briefTitle", ""),
                    "status": status_mod.get("overallStatus", ""),
                    "phase": ", ".join(phases) if phases else "N/A",
                    "conditions": cond_mod.get("conditions", []),
                    "brief_summary": desc_mod.get("briefSummary", ""),
                    "eligibility_criteria": elig_mod.get("eligibilityCriteria", ""),
                    "sponsor": spon_mod.get("leadSponsor", {}).get("name", ""),
                    "last_updated": status_mod.get("lastUpdatePostDateStruct", {}).get("date", ""),
                    "locations": locations,
                }

                if not trial["nct_id"]:
                    continue

                try:
                    # Add locations to Qdrant payload
                    await qdrant.upsert_trial(trial)
                    indexed += 1
                except Exception as e:
                    logger.warning("Failed to upsert %s: %s", trial["nct_id"], e)

            next_page_token = data.get("nextPageToken")
            if not next_page_token or indexed >= max_per_condition:
                break

    return indexed


async def main(conditions: list[str], max_per_condition: int) -> None:
    """Main seeding routine.

    Args:
        conditions: List of condition search terms.
        max_per_condition: Max trials per condition.
    """
    total = 0
    for condition in conditions:
        logger.info("Seeding: '%s' (max %d)…", condition, max_per_condition)
        count = await seed_for_condition(condition, max_per_condition)
        logger.info("  → Indexed %d trials for '%s'", count, condition)
        total += count

    logger.info("=" * 50)
    logger.info("Total trials indexed: %d", total)
    logger.info("Qdrant collection 'clinical_trials' is ready.")
    logger.info("Start the backend: uvicorn app.main:app --reload")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Qdrant with ClinicalTrials.gov data")
    parser.add_argument(
        "--conditions", nargs="+", default=DEFAULT_CONDITIONS,
        help="Disease conditions to fetch trials for"
    )
    parser.add_argument(
        "--max", type=int, default=50,
        help="Maximum trials to fetch per condition (default: 50)"
    )
    args = parser.parse_args()

    logger.info("OmniMatch Trial Seeder")
    logger.info("Conditions: %s", args.conditions)
    logger.info("Max per condition: %d", args.max)

    asyncio.run(main(args.conditions, args.max))
