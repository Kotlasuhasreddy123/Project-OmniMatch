"""Read-only NPPES registry checks. Never an authentication or license proof."""
from typing import Literal
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/credentials", tags=["Professional registry"])
REGISTRY_URL = "https://npiregistry.cms.hhs.gov/api/"


class RegistryRequest(BaseModel):
    npi: str = Field(pattern=r"^[12][0-9]{9}$")


class RegistryResult(BaseModel):
    status: Literal["record_found", "inactive", "organization", "not_found"]
    registry_name: str = ""
    specialty: str = ""
    source: str = "CMS NPPES, United States"
    identity_verified: bool = False
    license_verified: bool = False
    access_granted: bool = False
    message: str


def valid_npi(number: str) -> bool:
    digits = [int(c) for c in "80840" + number]
    return sum((d * 2 // 10 + d * 2 % 10) if (len(digits) - i) % 2 == 0 else d
               for i, d in enumerate(digits)) % 10 == 0


async def lookup_npi(npi: str) -> RegistryResult:
    if not valid_npi(npi):
        raise HTTPException(422, "Check the NPI number. Its check digit is not valid.")
    try:
        async with httpx.AsyncClient(timeout=8, trust_env=False, follow_redirects=False) as client:
            async with client.stream("GET", REGISTRY_URL, params={"version": "2.1", "number": npi}) as response:
                response.raise_for_status()
                content = bytearray()
                async for chunk in response.aiter_bytes():
                    content.extend(chunk)
                    if len(content) > 65536:
                        raise ValueError("Oversized registry response")
        import json
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("Malformed response")
        if data.get("Errors"):
            raise ValueError("Registry rejected lookup")
        results = data.get("results", [])
        if not isinstance(results, list):
            raise ValueError("Malformed results")
        if not results:
            return RegistryResult(status="not_found", message="No record found. Check the number or ask the owner to review your credentials.")
        record = results[0]
        if not isinstance(record, dict):
            raise ValueError("Malformed record")
        if str(record.get("number")) != npi:
            raise ValueError("Unexpected registry record")
        basic = record.get("basic", {})
        if not isinstance(basic, dict):
            raise ValueError("Malformed provider")
        name = " ".join(filter(None, [basic.get("first_name"), basic.get("last_name")]))
        taxonomies = record.get("taxonomies", [])
        if not isinstance(taxonomies, list) or any(not isinstance(t, dict) for t in taxonomies):
            raise ValueError("Malformed taxonomies")
        primary = next((t for t in taxonomies if t.get("primary")), {})
        if record.get("enumeration_type") != "NPI-1":
            return RegistryResult(status="organization", message="This number identifies an organization, not an individual professional.")
        if basic.get("status") != "A":
            return RegistryResult(status="inactive", registry_name=name[:200], message="The registry record is inactive. Owner review is required.")
        return RegistryResult(status="record_found", registry_name=name[:200], specialty=str(primary.get("desc", ""))[:200],
            message="An active individual registry record was found. This does not verify your identity or license and does not grant account access.")
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        raise HTTPException(503, "The registry is unavailable. No verification or access was granted. Try again later or ask the owner for review.")


@router.post("/npi", response_model=RegistryResult)
async def check_registry(body: RegistryRequest) -> RegistryResult:
    """Only the NPI is sent to CMS. Do not persist names, phone numbers or ID cards."""
    return await lookup_npi(body.npi)
