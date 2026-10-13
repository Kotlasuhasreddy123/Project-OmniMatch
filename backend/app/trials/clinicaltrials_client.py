"""ClinicalTrials.gov API v2 client for fetching and syncing trial data."""

from __future__ import annotations

import logging
from typing import AsyncIterator

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

FIELDS = [
    "NCTId",
    "BriefTitle",
    "OverallStatus",
    "Phase",
    "Condition",
    "BriefSummary",
    "EligibilityCriteria",
    "LeadSponsorName",
    "LastUpdatePostDate",
]


class ClinicalTrialsClient:
    """Async HTTP client for ClinicalTrials.gov API v2.

    Fetches studies in pages and yields structured trial dicts.
    """

    def __init__(self) -> None:
        self.base_url = settings.clinicaltrials_api_base
        self.page_size = settings.clinicaltrials_sync_page_size
        self.max_studies = settings.clinicaltrials_max_studies

    async def iter_studies(self) -> AsyncIterator[dict]:
        """Fetch studies from ClinicalTrials.gov API, yielding one dict per study.

        Paginates automatically using nextPageToken until max_studies is reached.

        Yields:
            Dict with normalized trial fields for Qdrant indexing.
        """
        fetched = 0
        next_page_token: str | None = None

        async with httpx.AsyncClient(timeout=30.0) as client:
            while fetched < self.max_studies:
                params: dict = {
                    "format": "json",
                    "pageSize": min(self.page_size, self.max_studies - fetched),
                    "fields": "|".join(FIELDS),
                    "filter.overallStatus": "RECRUITING",
                }
                if next_page_token:
                    params["pageToken"] = next_page_token

                try:
                    response = await client.get(self.base_url, params=params)
                    response.raise_for_status()
                except httpx.HTTPStatusError as exc:
                    logger.error("ClinicalTrials API error: %s", exc)
                    break
                except httpx.RequestError as exc:
                    logger.error("ClinicalTrials network error: %s", exc)
                    break

                data = response.json()
                studies = data.get("studies", [])

                if not studies:
                    break

                for study in studies:
                    protocol = study.get("protocolSection", {})
                    id_module = protocol.get("identificationModule", {})
                    status_module = protocol.get("statusModule", {})
                    desc_module = protocol.get("descriptionModule", {})
                    eligibility_module = protocol.get("eligibilityModule", {})
                    conditions_module = protocol.get("conditionsModule", {})
                    sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
                    design_module = protocol.get("designModule", {})

                    phases = design_module.get("phases", [])
                    phase_str = ", ".join(phases) if phases else "N/A"

                    yield {
                        "nct_id": id_module.get("nctId", ""),
                        "title": id_module.get("briefTitle", ""),
                        "status": status_module.get("overallStatus", ""),
                        "phase": phase_str,
                        "conditions": conditions_module.get("conditions", []),
                        "brief_summary": desc_module.get("briefSummary", ""),
                        "eligibility_criteria": eligibility_module.get("eligibilityCriteria", ""),
                        "sponsor": sponsor_module.get("leadSponsor", {}).get("name", ""),
                        "last_updated": status_module.get("lastUpdatePostDateStruct", {}).get("date", ""),
                    }
                    fetched += 1
                    if fetched >= self.max_studies:
                        break

                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break

        logger.info("ClinicalTrials sync: fetched %d studies", fetched)
