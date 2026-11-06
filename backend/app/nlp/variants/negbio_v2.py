"""Unused rule experiment under a legacy NegBio-inspired filename.

This is a heuristic window implementation, not the original NegBio package,
and it does not load a dependency parser or trained spaCy model. Published
NegBio results must not be attributed to this code. The live extraction
endpoint does not call it. Measure this implementation separately.
"""

from __future__ import annotations
import re
from functools import lru_cache

# NegBio-style trigger sets with dependency scope labels
# Based on Universal Dependencies negation patterns

NEGATION_HEADS = {
    "no", "not", "never", "neither", "nor", "without", "absent",
    "deny", "denies", "denied", "exclude", "excludes", "excluded",
    "negative", "rule", "rules", "ruled", "fail", "fails", "failed",
}

UNCERTAINTY_HEADS = {
    "possible", "possibly", "probable", "probably", "likely", "unlikely",
    "suspect", "suspected", "cannot", "uncertain", "questionable",
    "evaluate", "r/o", "rule out", "concern for",
}

FAMILY_HEADS = {
    "mother", "father", "sister", "brother", "parent", "parents",
    "grandmother", "grandfather", "sibling", "family", "familial",
    "hereditary", "heritable", "genetic",
}

# Extended window for dependency-style checking (larger than NegEx)
DEP_WINDOW = 12

_NEGATION_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(h) for h in NEGATION_HEADS) + r")\b",
    re.IGNORECASE
)
_UNCERTAINTY_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(h) for h in UNCERTAINTY_HEADS) + r")\b",
    re.IGNORECASE
)
_FAMILY_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(h) for h in FAMILY_HEADS) + r")\b",
    re.IGNORECASE
)

# Long-distance patterns NegEx misses (NegBio's key contribution)
LONG_DISTANCE_PATTERNS = [
    re.compile(r"\bdid\s+not\s+(?:show|reveal|demonstrate|indicate|find)\b", re.IGNORECASE),
    re.compile(r"\bno\s+(?:sign|signs|finding|findings|evidence|indication)\s+of\b", re.IGNORECASE),
    re.compile(r"\bnot\s+(?:consistent|consistent\s+with|suggestive\s+of)\b", re.IGNORECASE),
    re.compile(r"\bwithout\s+(?:any\s+)?(?:evidence|signs?|findings?)\s+of\b", re.IGNORECASE),
    re.compile(r"\b(?:failed|fails)\s+to\s+(?:show|demonstrate|reveal)\b", re.IGNORECASE),
    re.compile(r"\bcannot\s+(?:be\s+)?(?:ruled?\s+out|excluded)\b", re.IGNORECASE),
]


def classify(text: str, entity_start: int, entity_end: int) -> dict:
    """Classify negation using NegBio-style extended dependency window.

    Key improvement over NegEx: larger window + long-distance pattern matching
    catches constructions like 'did not reveal any evidence of diabetes'.

    Args:
        text: Full transcription text.
        entity_start: Character start of entity.
        entity_end: Character end of entity.

    Returns:
        dict with negated (bool), context (str), confidence (float),
        uncertainty (bool).
    """
    before_words = text[:entity_start].split()
    after_words = text[entity_end:].split()
    before = " ".join(before_words[-DEP_WINDOW:])
    after = " ".join(after_words[:DEP_WINDOW])
    context_text = before + " " + after

    # Family context — highest priority
    if _FAMILY_PATTERN.search(before):
        return {"negated": False, "context": "family", "confidence": 0.91, "uncertainty": False}

    # Long-distance negation (NegBio's key innovation)
    sentence_before = text[max(0, entity_start - 200):entity_start]
    if any(p.search(sentence_before) for p in LONG_DISTANCE_PATTERNS):
        return {"negated": True, "context": "patient", "confidence": 0.93, "uncertainty": False}

    # Standard negation
    if _NEGATION_PATTERN.search(before):
        return {"negated": True, "context": "patient", "confidence": 0.91, "uncertainty": False}

    if _NEGATION_PATTERN.search(after):
        return {"negated": True, "context": "patient", "confidence": 0.87, "uncertainty": False}

    # Uncertainty (NegBio distinguishes this from negation)
    if _UNCERTAINTY_PATTERN.search(context_text):
        return {"negated": False, "context": "hypothetical", "confidence": 0.79, "uncertainty": True}

    return {"negated": False, "context": "patient", "confidence": 0.94, "uncertainty": False}
