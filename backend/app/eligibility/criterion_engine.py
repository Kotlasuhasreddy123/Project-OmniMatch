"""Per-criterion eligibility scoring engine — NEW FEATURE differentiating OmniMatch.

Existing systems (TrialMatchAI, PRISM, TrialGPT) return a single similarity score.
OmniMatch evaluates each eligibility criterion individually and produces:
  1. A per-criterion verdict: MET | NOT_MET | MISSING | UNKNOWN
  2. A composite Enrollment Readiness score (0–100%)

This is the primary differentiating capability vs. all existing clinical trial
matching systems as of 2025.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal

logger = logging.getLogger(__name__)


class CriterionVerdict(str, Enum):
    MET = "MET"           # Entity found in transcript, affirmed, approved by staff
    NOT_MET = "NOT_MET"   # Entity found as negated OR excluded by staff
    MISSING = "MISSING"   # Criterion not mentioned in visit at all
    UNKNOWN = "UNKNOWN"   # Lab value / biomarker required but not spoken


@dataclass
class CriterionResult:
    """Result of evaluating one eligibility criterion against a patient session."""
    criterion_text: str
    verdict: CriterionVerdict
    matched_entity: str | None = None       # The patient entity that matched
    confidence: float = 0.0                 # 0.0–1.0
    is_inclusion: bool = True               # True = inclusion, False = exclusion
    explanation: str = ""


@dataclass
class EligibilityBreakdown:
    """Full per-criterion breakdown for one trial match."""
    nct_id: str
    title: str
    criteria_results: list[CriterionResult] = field(default_factory=list)
    met_count: int = 0
    not_met_count: int = 0
    missing_count: int = 0
    unknown_count: int = 0
    enrollment_readiness_score: float = 0.0  # 0–100 composite score
    score_explanation: str = ""


# ---------------------------------------------------------------------------
# Lab/biomarker patterns — these require values not spoken → UNKNOWN
# ---------------------------------------------------------------------------
LAB_PATTERNS = [
    r"\bhba1c\b", r"\ba1c\b", r"\bglucose\b", r"\bldl\b", r"\bhdl\b",
    r"\bcholesterol\b", r"\bcreatinine\b", r"\begfr\b", r"\bbun\b",
    r"\bhemoglobin\b", r"\bplatelet\b", r"\bwbc\b", r"\bpsa\b",
    r"\btsh\b", r"\bbmi\b", r"\bblood\s+pressure\b",
    r"\btroponin\b", r"\bneutrophil\b", r"\blymphocyte\b",
    r"\balt\b", r"\bast\b", r"\bbilirubin\b",
]

# Age criteria patterns
AGE_PATTERN = re.compile(
    r"(\d+)\s*(?:years?|yrs?)?\s*(?:of\s+age|old)?\s*(?:to|–|-|and)\s*(\d+)|"
    r"(?:aged?|age)\s*(?:between\s*)?(\d+)\s*(?:to|–|-|and)\s*(\d+)|"
    r"(?:≥|>=|at\s+least)\s*(\d+)\s*(?:years?)?|"
    r"(?:≤|<=|no\s+more\s+than|less\s+than)\s*(\d+)\s*(?:years?)?",
    re.IGNORECASE,
)


def _is_lab_criterion(text: str) -> bool:
    """Return True if the criterion requires a lab value."""
    return any(re.search(p, text, re.IGNORECASE) for p in LAB_PATTERNS)


def _is_exclusion_section(section_text: str) -> bool:
    """Return True if the text is part of an Exclusion Criteria section."""
    return bool(re.search(r"\bexclusion\b", section_text, re.IGNORECASE))


def _split_criteria(eligibility_text: str) -> tuple[list[str], list[str]]:
    """Split eligibility text into inclusion and exclusion criterion lines.

    Args:
        eligibility_text: Raw eligibility criteria text from ClinicalTrials.gov.

    Returns:
        Tuple of (inclusion_criteria, exclusion_criteria) as string lists.
    """
    inclusion: list[str] = []
    exclusion: list[str] = []

    # Split at Inclusion/Exclusion section headers
    parts = re.split(
        r"(?i)(inclusion\s+criteria|exclusion\s+criteria)",
        eligibility_text
    )

    current_section = "inclusion"
    for part in parts:
        if re.match(r"(?i)exclusion\s+criteria", part):
            current_section = "exclusion"
            continue
        if re.match(r"(?i)inclusion\s+criteria", part):
            current_section = "inclusion"
            continue

        # Split section into individual criteria lines
        lines = re.split(r"\n|\*\s+|•\s+|;\s*|\d+\.\s+", part)
        for line in lines:
            clean = line.strip().strip("*•-")
            # Short criteria such as "HbA1c > 7.5%" are clinically material
            # and must reach the UNKNOWN lab-value classifier.
            if len(clean) >= 3:
                if current_section == "inclusion":
                    inclusion.append(clean)
                else:
                    exclusion.append(clean)

    return inclusion, exclusion


def _match_criterion_to_entities(
    criterion: str,
    approved_terms: list[str],
    negated_terms: list[str],
    all_terms: list[str],
) -> CriterionResult:
    """Evaluate a single eligibility criterion against patient entities.

    Args:
        criterion: One eligibility criterion line.
        approved_terms: Staff-approved, patient-context entity terms.
        negated_terms: Negated entity terms from the session.
        all_terms: All extracted terms (approved + rejected + negated).

    Returns:
        CriterionResult with verdict, matched entity, and explanation.
    """
    criterion_lower = criterion.lower()

    # Check for lab/biomarker requirement → UNKNOWN
    if _is_lab_criterion(criterion_lower):
        return CriterionResult(
            criterion_text=criterion,
            verdict=CriterionVerdict.UNKNOWN,
            confidence=0.5,
            explanation="Requires a lab value or biomarker not captured in ambient audio.",
        )

    # Check if any approved term appears in this criterion → MET
    for term in approved_terms:
        if term.lower() in criterion_lower:
            return CriterionResult(
                criterion_text=criterion,
                verdict=CriterionVerdict.MET,
                matched_entity=term,
                confidence=0.85,
                explanation=f"'{term}' was approved by clinical staff and matches this criterion.",
            )

    # Check if any negated term appears in this criterion → NOT_MET
    for term in negated_terms:
        if term.lower() in criterion_lower:
            return CriterionResult(
                criterion_text=criterion,
                verdict=CriterionVerdict.NOT_MET,
                matched_entity=term,
                confidence=0.80,
                explanation=f"'{term}' was detected as negated in the patient transcript.",
            )

    # Check if any term (any status) appears but was not approved → MISSING
    for term in all_terms:
        if term.lower() in criterion_lower:
            return CriterionResult(
                criterion_text=criterion,
                verdict=CriterionVerdict.MISSING,
                matched_entity=term,
                confidence=0.6,
                explanation=f"'{term}' was detected but not approved by staff for matching.",
            )

    # Not mentioned at all → MISSING
    return CriterionResult(
        criterion_text=criterion,
        verdict=CriterionVerdict.MISSING,
        confidence=0.0,
        explanation="This criterion was not addressed in the patient visit transcript.",
    )


def compute_enrollment_readiness(
    inclusion_results: list[CriterionResult],
    exclusion_results: list[CriterionResult],
    similarity_score: float,
) -> tuple[float, str]:
    """Compute the composite Enrollment Readiness Score (0–100).

    Formula:
        score = (similarity_score * 0.35)
              + (inclusion_met_rate * 0.45)
              - (exclusion_violated_penalty * 0.20)

    Args:
        inclusion_results: Per-criterion results for inclusion criteria.
        exclusion_results: Per-criterion results for exclusion criteria.
        similarity_score: Qdrant cosine similarity (0.0–1.0).

    Returns:
        Tuple of (score_0_to_100, explanation_string).
    """
    if not inclusion_results:
        return round(similarity_score * 35, 1), "Score based on semantic similarity only (no structured criteria parsed)."

    # Inclusion met rate (MET / total non-UNKNOWN)
    evaluable = [r for r in inclusion_results if r.verdict != CriterionVerdict.UNKNOWN]
    met = [r for r in evaluable if r.verdict == CriterionVerdict.MET]
    inclusion_rate = len(met) / len(evaluable) if evaluable else 0.0

    # Exclusion violated penalty (exclusion NOT_MET means the patient HAS an exclusion criterion)
    exclusion_violated = [r for r in exclusion_results if r.verdict == CriterionVerdict.MET]
    exclusion_penalty = min(1.0, len(exclusion_violated) * 0.25)  # 25% penalty per violation

    raw = (
        (similarity_score * 0.35)
        + (inclusion_rate * 0.45)
        - (exclusion_penalty * 0.20)
    )
    score = round(max(0.0, min(1.0, raw)) * 100, 1)

    explanation = (
        f"Semantic similarity: {round(similarity_score * 100)}% (×0.35) | "
        f"Inclusion met: {len(met)}/{len(evaluable)} (×0.45) | "
        f"Exclusion violations: {len(exclusion_violated)} (−{round(exclusion_penalty * 20)}pts)"
    )

    return score, explanation


def evaluate_trial_eligibility(
    nct_id: str,
    title: str,
    eligibility_text: str,
    similarity_score: float,
    approved_terms: list[str],
    negated_terms: list[str],
    all_terms: list[str],
) -> EligibilityBreakdown:
    """Perform full per-criterion eligibility evaluation for one trial.

    This is the core differentiating algorithm of OmniMatch vs. all
    existing clinical trial matching systems.

    Args:
        nct_id: ClinicalTrials.gov NCT ID.
        title: Trial brief title.
        eligibility_text: Raw eligibility criteria from the trial record.
        similarity_score: Qdrant cosine similarity score.
        approved_terms: Staff-approved, patient-context entity terms (lowercase).
        negated_terms: Negated entity terms from NLP pipeline (lowercase).
        all_terms: All entity terms extracted from the session (lowercase).

    Returns:
        EligibilityBreakdown with per-criterion results and composite score.
    """
    inclusion_lines, exclusion_lines = _split_criteria(eligibility_text)

    inclusion_results = [
        _match_criterion_to_entities(
            c, approved_terms, negated_terms, all_terms
        )
        for c in inclusion_lines[:15]  # cap at 15 for performance
    ]
    for r in inclusion_results:
        r.is_inclusion = True

    exclusion_results = [
        _match_criterion_to_entities(
            c, approved_terms, negated_terms, all_terms
        )
        for c in exclusion_lines[:10]
    ]
    for r in exclusion_results:
        r.is_inclusion = False

    all_results = inclusion_results + exclusion_results

    met = sum(1 for r in all_results if r.verdict == CriterionVerdict.MET)
    not_met = sum(1 for r in all_results if r.verdict == CriterionVerdict.NOT_MET)
    missing = sum(1 for r in all_results if r.verdict == CriterionVerdict.MISSING)
    unknown = sum(1 for r in all_results if r.verdict == CriterionVerdict.UNKNOWN)

    score, explanation = compute_enrollment_readiness(
        inclusion_results, exclusion_results, similarity_score
    )

    return EligibilityBreakdown(
        nct_id=nct_id,
        title=title,
        criteria_results=all_results,
        met_count=met,
        not_met_count=not_met,
        missing_count=missing,
        unknown_count=unknown,
        enrollment_readiness_score=score,
        score_explanation=explanation,
    )
