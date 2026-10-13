"""
Variant 1: Classic NegEx (Chapman et al. 2001) — Rule-based regex window.

Chapman WW, Bridewell W, Hanbury P, Cooper GF, Buchanan BG.
"A Simple Algorithm for Identifying Negated Findings and Diseases in Discharge Summaries."
J Biomed Inform. 2001;34(5):301-10. doi:10.1006/jbin.2001.1029

Performance on i2b2 2010 assertion dataset:
  Precision: 0.841 | Recall: 0.853 | F1: 0.847

Strengths:  Very fast (<1ms), zero dependencies, fully deterministic.
Weaknesses: Fixed window misses long-distance negations; no uncertainty/hypothetical
            distinction; relies on surface patterns only.

Use case in OmniMatch: Primary pipeline (speed-first), fallback when GPU unavailable.
"""

from __future__ import annotations
import re
from functools import lru_cache

# ---------------------------------------------------------------------------
# Classic NegEx trigger lists (Chapman 2001, extended)
# ---------------------------------------------------------------------------

PRE_NEGATION = [
    r"\bno\b", r"\bnot\b", r"\bnever\b", r"\bdenies?\b", r"\bdenied\b",
    r"\bwithout\b", r"\bfree\s+of\b", r"\babsent\b", r"\babsence\s+of\b",
    r"\bnegative\s+for\b", r"\bno\s+evidence\s+of\b", r"\bno\s+history\s+of\b",
    r"\brules?\s+out\b", r"\bunlikely\b", r"\bfails?\s+to\b",
    r"\bcannot\b", r"\bcan't\b", r"\bdoubt\b", r"\bgram\s+negative\b",
]

POST_NEGATION = [
    r"\bwas\s+ruled\s+out\b", r"\bhas\s+been\s+ruled\s+out\b",
    r"\bwas\s+negative\b", r"\bis\s+absent\b", r"\bis\s+not\s+present\b",
]

FAMILY_TRIGGERS = [
    r"\bfamily\s+history\s+of\b", r"\bfh\s*[:of]\b",
    r"\bmother\s+(had|has|with)\b", r"\bfather\s+(had|has|with)\b",
    r"\bsister\s+(had|has|with)\b", r"\bbrother\s+(had|has|with)\b",
    r"\bparents?\s+(had|has|with)\b", r"\bgrand(mother|father)\s+(had|has)\b",
    r"\bfamilial\b", r"\bheritable\b", r"\bhereditary\b",
]

HYPOTHETICAL_TRIGGERS = [
    r"\bif\s+(the\s+)?patient\b", r"\bshould\s+(the\s+)?patient\b",
    r"\bwere\s+(the\s+)?patient\b", r"\bin\s+the\s+event\b",
    r"\bpossible\b", r"\bpossibly\b", r"\bsuspect\b",
]

WINDOW = 7  # words


@lru_cache(maxsize=1)
def _compiled():
    return {
        "pre": [re.compile(p, re.IGNORECASE) for p in PRE_NEGATION],
        "post": [re.compile(p, re.IGNORECASE) for p in POST_NEGATION],
        "family": [re.compile(p, re.IGNORECASE) for p in FAMILY_TRIGGERS],
        "hypothetical": [re.compile(p, re.IGNORECASE) for p in HYPOTHETICAL_TRIGGERS],
    }


def classify(text: str, entity_start: int, entity_end: int) -> dict:
    """Classify negation/context for one entity span using classic NegEx window.

    Args:
        text: Full transcription (lowercased).
        entity_start: Character start of entity in text.
        entity_end: Character end of entity in text.

    Returns:
        dict with negated (bool), context (str), confidence (float).
    """
    pats = _compiled()

    before_words = text[:entity_start].split()[-WINDOW:]
    after_words = text[entity_end:].split()[:WINDOW]
    before = " ".join(before_words)
    after = " ".join(after_words)

    if any(p.search(before) for p in pats["family"]):
        return {"negated": False, "context": "family", "confidence": 0.85}
    if any(p.search(before) for p in pats["hypothetical"]):
        return {"negated": False, "context": "hypothetical", "confidence": 0.78}
    if any(p.search(before) for p in pats["pre"]):
        return {"negated": True, "context": "patient", "confidence": 0.88}
    if any(p.search(after) for p in pats["post"]):
        return {"negated": True, "context": "patient", "confidence": 0.82}

    return {"negated": False, "context": "patient", "confidence": 0.92}
