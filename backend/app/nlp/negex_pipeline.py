"""NegEx-based NLP pipeline for clinical entity extraction with negation detection.

Implements REQ-03: extracts clinical entities and classifies negations/family context.
Target: ≥ 95% negation detection accuracy on test transcripts.
"""

from __future__ import annotations

import logging
import re
from functools import lru_cache

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Negation trigger patterns (NegEx algorithm)
# ---------------------------------------------------------------------------

# Pre-negation triggers — appear BEFORE the entity
PRE_NEGATION_TRIGGERS = [
    r"\bno\b",
    r"\bnot\b",
    r"\bdenies\b",
    r"\bdenied\b",
    r"\bwithout\b",
    r"\brules?\s+out\b",
    r"\bno\s+history\s+of\b",
    r"\bnegative\s+for\b",
    r"\bnever\b",
    r"\bfree\s+of\b",
    r"\babsence\s+of\b",
    r"\bno\s+evidence\s+of\b",
    r"\bunlikely\b",
]

# Post-negation triggers — appear AFTER the entity
POST_NEGATION_TRIGGERS = [
    r"\bwas\s+ruled\s+out\b",
    r"\bhas\s+been\s+ruled\s+out\b",
    r"\bwas\s+negative\b",
    r"\bis\s+absent\b",
]

# Family history context triggers
FAMILY_CONTEXT_TRIGGERS = [
    r"\bfamily\s+history\s+of\b",
    r"\bfamily\s+history(?:\s+\w+){0,3}\s+for\b",
    r"\bmother\s+(had|has|with)\b",
    r"\bfather\s+(had|has|with)\b",
    r"\bsister\s+(had|has|with)\b",
    r"\bbrother\s+(had|has|with)\b",
    r"\bparent[s]?\s+(had|has|with)\b",
    r"\bgrandmother\s+(had|has|with)\b",
    r"\bgrandfather\s+(had|has|with)\b",
    r"\bfamilial\b",
]

# Hypothetical context triggers
HYPOTHETICAL_TRIGGERS = [
    r"\bif\s+(the\s+)?patient\b",
    r"\bshould\s+(the\s+)?patient\b",
    r"\bwere\s+(the\s+)?patient\b",
    r"\bhypothetically\b",
]

# ---------------------------------------------------------------------------
# Medical entity patterns (simplified NER without spaCy model requirement)
# ---------------------------------------------------------------------------

DISEASE_PATTERNS = [
    r"\b(diabetes(?:\s+mellitus)?(?:\s+type\s+[12])?)\b",
    r"\b(hypertension|high\s+blood\s+pressure)\b",
    r"\b(asthma|copd|emphysema|bronchitis)\b",
    r"\b(cancer|carcinoma|tumor|neoplasm|malignancy)\b",
    r"\b(heart\s+(?:disease|failure|attack)|myocardial\s+infarction|mi)\b",
    r"\b(stroke|tia|transient\s+ischemic\s+attack)\b",
    r"\b(depression|anxiety|bipolar|schizophrenia|ptsd)\b",
    r"\b(arthritis|rheumatoid|osteoarthritis|lupus|fibromyalgia)\b",
    r"\b(hypothyroidism|hyperthyroidism|thyroid\s+disease)\b",
    r"\b(kidney\s+disease|renal\s+failure|ckd|esrd)\b",
    r"\b(liver\s+disease|cirrhosis|hepatitis\s+[abc])\b",
    r"\b(alzheimer|dementia|parkinson)\b",
    r"\b(epilepsy|seizures?)\b",
    r"\b(obesity|overweight|bmi\s+>\s*\d+)\b",
    r"\b(anemia|sickle\s+cell|thalassemia)\b",
    r"\b(hiv|aids)\b",
    r"\b(crohn|colitis|ibd|irritable\s+bowel)\b",
    r"\b(multiple\s+sclerosis|ms)\b",
    r"\b(psoriasis|eczema|atopic\s+dermatitis)\b",
    r"\b(migraines?|chronic\s+headaches?)\b",
]

SYMPTOM_PATTERNS = [
    r"\b(chest\s+pain|chest\s+tightness|angina)\b",
    r"\b(shortness\s+of\s+breath|dyspnea|sob)\b",
    r"\b(fatigue|tiredness|exhaustion|lethargy)\b",
    r"\b(dizziness|vertigo|lightheadedness)\b",
    r"\b(nausea|vomiting|emesis)\b",
    r"\b(fever|pyrexia|elevated\s+temperature)\b",
    r"\b(cough(?:ing)?|persistent\s+cough)\b",
    r"\b(pain|aching|soreness|discomfort)\b",
    r"\b(swelling|edema|bloating)\b",
    r"\b(insomnia|sleep\s+(?:problems?|difficulties|disorder))\b",
    r"\b(weight\s+(?:loss|gain))\b",
    r"\b(blurred?\s+vision|vision\s+(?:changes?|loss))\b",
    r"\b(tingling|numbness|paresthesia)\b",
    r"\b(palpitations?|irregular\s+heartbeat)\b",
]

MEDICATION_PATTERNS = [
    r"\b(metformin|insulin|glipizide|glimepiride)\b",
    r"\b(lisinopril|amlodipine|metoprolol|atenolol|losartan|valsartan)\b",
    r"\b(atorvastatin|simvastatin|rosuvastatin|pravastatin)\b",
    r"\b(aspirin|ibuprofen|naproxen|acetaminophen|tylenol|advil)\b",
    r"\b(omeprazole|pantoprazole|lansoprazole|esomeprazole)\b",
    r"\b(albuterol|fluticasone|budesonide|salmeterol)\b",
    r"\b(sertraline|fluoxetine|paroxetine|escitalopram|citalopram)\b",
    r"\b(warfarin|apixaban|rivaroxaban|dabigatran|clopidogrel)\b",
    r"\b(levothyroxine|synthroid)\b",
    r"\b(prednisone|prednisolone|dexamethasone)\b",
    r"\b(amoxicillin|azithromycin|ciprofloxacin|doxycycline)\b",
    r"\b(gabapentin|pregabalin|duloxetine|amitriptyline)\b",
]

LAB_VALUE_PATTERNS = [
    r"\b(a1c|hba1c)\s*(?:of\s*)?\d+\.?\d*\s*%?",
    r"\b(blood\s+sugar|glucose|fasting\s+glucose)\s*(?:of\s*)?\d+",
    r"\b(blood\s+pressure|bp)\s*(?:of\s*)?\d+/\d+",
    r"\b(cholesterol|ldl|hdl|triglycerides)\s*(?:of\s*)?\d+",
    r"\b(creatinine|egfr|bun)\s*(?:of\s*)?\d+",
    r"\b(hemoglobin|hgb|wbc|platelet\s+count)\s*(?:of\s*)?\d+",
    r"\b(tsh|t3|t4)\s*(?:of\s*)?\d+\.?\d*",
    r"\b(psa)\s*(?:of\s*)?\d+\.?\d*",
    r"\bbmi\s*(?:of\s*)?\d+\.?\d*",
]

PROCEDURE_PATTERNS = [
    r"\b(colonoscopy|endoscopy|biopsy)\b",
    r"\b(mri|ct\s+scan|x-?ray|ultrasound|echocardiogram)\b",
    r"\b(surgery|operation|procedure|resection)\b",
    r"\b(chemotherapy|radiation\s+therapy|immunotherapy)\b",
    r"\b(dialysis|hemodialysis)\b",
    r"\b(catheterization|angioplasty|stenting)\b",
    r"\b(transplant(?:ation)?)\b",
    r"\b(physical\s+therapy|occupational\s+therapy)\b",
]

ALL_ENTITY_PATTERNS = {
    "DISEASE": DISEASE_PATTERNS,
    "SYMPTOM": SYMPTOM_PATTERNS,
    "MEDICATION": MEDICATION_PATTERNS,
    "LAB_VALUE": LAB_VALUE_PATTERNS,
    "PROCEDURE": PROCEDURE_PATTERNS,
}

# Context window: number of words to look before/after entity for triggers
NEGATION_WINDOW = 6


def _compile_patterns(patterns: list[str]) -> list[re.Pattern]:
    """Compile a list of regex pattern strings into Pattern objects."""
    return [re.compile(p, re.IGNORECASE) for p in patterns]


@lru_cache(maxsize=1)
def _get_compiled_patterns():
    """Return cached compiled regex pattern groups."""
    return {
        "entity": {etype: _compile_patterns(pats) for etype, pats in ALL_ENTITY_PATTERNS.items()},
        "pre_negation": _compile_patterns(PRE_NEGATION_TRIGGERS),
        "post_negation": _compile_patterns(POST_NEGATION_TRIGGERS),
        "family_context": _compile_patterns(FAMILY_CONTEXT_TRIGGERS),
        "hypothetical": _compile_patterns(HYPOTHETICAL_TRIGGERS),
    }


def _check_context(
    text: str,
    match_start: int,
    match_end: int,
    trigger_patterns: list[re.Pattern],
    window: int = NEGATION_WINDOW,
    look_before: bool = True,
    look_after: bool = False,
) -> bool:
    """Check if a trigger pattern appears within a word-window around the entity match.

    Args:
        text: Full transcription text.
        match_start: Start index of the entity match.
        match_end: End index of the entity match.
        trigger_patterns: Compiled regex patterns to search for.
        window: Number of words to look before/after.
        look_before: Whether to check text before the entity.
        look_after: Whether to check text after the entity.

    Returns:
        True if any trigger pattern is found within the context window.
    """
    # Negation cannot reach across sentences or a contrast such as "but".
    before_scope = re.split(r"[.!?;]|\b(?:but|however|although)\b", text[:match_start])[-1]
    after_scope = re.split(r"[.!?;]|\b(?:but|however|although)\b", text[match_end:])[0]
    words_before = before_scope.split()[-window:]
    words_after = after_scope.split()[:window]

    context_text = ""
    if look_before:
        context_text += " ".join(words_before) + " "
    if look_after:
        context_text += " " + " ".join(words_after)

    return any(pat.search(context_text) for pat in trigger_patterns)


def extract_entities(transcription: str) -> list[dict]:
    """Extract clinical entities from a transcription with negation and context classification.

    Implements the NegEx algorithm to detect:
    - Negated entities (should be excluded from Qdrant queries)
    - Family history context (excluded from patient match)
    - Hypothetical context (excluded from patient match)
    - Affirmed patient entities (included in match queries)

    Args:
        transcription: The raw clinical transcription text.

    Returns:
        List of entity dicts with keys:
        term, entity_type, negated, context, confidence, status
    """
    if not transcription or not transcription.strip():
        return []

    patterns = _get_compiled_patterns()
    text = transcription.lower()
    found_entities: list[dict] = []
    seen_terms: set[str] = set()  # deduplicate

    for entity_type, entity_patterns in patterns["entity"].items():
        for pat in entity_patterns:
            for match in pat.finditer(text):
                term = match.group(0).strip()
                normalized_term = re.sub(r"\s+", " ", term)

                start, end = match.start(), match.end()

                # Keep family-history scope within the current sentence. A
                # short fixed word window misses coordinated mentions such as
                # "family history significant for diabetes in mother and
                # hypertension in father".
                sentence_start = max(text.rfind(".", 0, start), text.rfind("!", 0, start), text.rfind("?", 0, start)) + 1
                sentence_prefix = text[sentence_start:start]
                # "Family history ..., but the patient has ..." changes the
                # subject back to the patient within a single sentence.
                sentence_prefix = re.split(
                    r"\b(?:but|however|patient\s+(?:herself|himself|has|is))\b",
                    sentence_prefix,
                )[-1]

                # Determine context: family history takes priority
                is_family = any(pat.search(sentence_prefix) for pat in patterns["family_context"])
                is_hypothetical = _check_context(
                    text, start, end, patterns["hypothetical"], look_before=True
                )
                is_negated = _check_context(
                    text, start, end, patterns["pre_negation"], look_before=True
                ) or _check_context(
                    text, start, end, patterns["post_negation"], look_after=True
                )
                before_scope = re.split(r"[.!?;]|\bbut\b", text[:start])[-1]
                if re.search(r"\b(?:does|do|did)\s+not\s+deny\b", before_scope):
                    is_negated = False

                # Retain the same term when it occurs with different contexts
                # (for example a family history followed by a patient finding).
                entity_key = f"{normalized_term}|{is_family}|{is_negated}"
                if entity_key in seen_terms:
                    continue
                seen_terms.add(entity_key)

                # Determine context label
                if is_family:
                    context = "family"
                elif is_hypothetical:
                    context = "hypothetical"
                else:
                    context = "patient"

                # Confidence heuristic: longer, more specific matches score higher
                confidence = min(0.95, 0.6 + len(normalized_term.split()) * 0.08)
                if is_negated or is_family:
                    confidence = max(0.5, confidence - 0.1)

                found_entities.append({
                    "term": normalized_term,
                    "entity_type": entity_type,
                    "negated": is_negated,
                    "context": context,
                    "confidence": round(confidence, 3),
                    "status": "pending",
                })

    # Sort by confidence descending
    found_entities.sort(key=lambda e: e["confidence"], reverse=True)
    return found_entities
