"""Trial Freshness Gate for safe coordinator outreach.

A semantic match is not an enrollment decision.  This gate makes registry
recency, recruiting status, and site visibility explicit before a coordinator
is asked to act on a match.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

FRESH_DAYS = 30
REVIEW_DAYS = 90
ACTIVE_STATUSES = {"RECRUITING", "NOT_YET_RECRUITING", "ENROLLING_BY_INVITATION"}


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None


def evaluate_trial_freshness(
    *, status: str, last_updated: str, locations: list[dict], today: date | None = None
) -> dict:
    """Return an explainable gate for outreach, never a clinical eligibility claim."""
    today = today or datetime.now(timezone.utc).date()
    parsed = _parse_date(last_updated)
    age_days = (today - parsed).days if parsed else None
    active = status.upper() in ACTIVE_STATUSES
    has_site_data = bool(locations)

    if not active:
        level, action = "BLOCKED", "DO_NOT_ROUTE"
        reason = f"Registry status is {status or 'unknown'}, not an active enrollment state."
    elif age_days is None or age_days > REVIEW_DAYS:
        level, action = "REVIEW", "VERIFY_BEFORE_OUTREACH"
        reason = "Registry record is missing a recent update date or is older than 90 days."
    elif not has_site_data:
        level, action = "REVIEW", "VERIFY_BEFORE_OUTREACH"
        reason = "No site location is available; verify a participating site before outreach."
    elif age_days > FRESH_DAYS:
        level, action = "REVIEW", "VERIFY_BEFORE_OUTREACH"
        reason = "Registry record is older than 30 days; confirm site-level availability."
    else:
        level, action = "READY", "ROUTE_TO_COORDINATOR"
        reason = "Registry status, update recency, and site data support coordinator review."

    return {
        "level": level,
        "recommended_action": action,
        "reason": reason,
        "registry_status": status or "UNKNOWN",
        "last_updated": last_updated or None,
        "age_days": age_days,
        "site_data_available": has_site_data,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }
