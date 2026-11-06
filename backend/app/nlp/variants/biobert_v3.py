"""Unused experimental zero-shot NLI wrapper, retained under a legacy filename.

The configured checkpoint is cross-encoder/nli-MiniLM2-L6-H768, NOT BioBERT.
The live /nlp/extract endpoint does not call this module, and NLP_VARIANT is
not a wired configuration switch. No local medical accuracy or latency is
established for this wrapper. It can fall back to a rule experiment when its
optional dependency/model is unavailable. No project fine-tuning is performed.
"""

from __future__ import annotations
import logging
import re
from typing import Literal

logger = logging.getLogger(__name__)

AssertionType = Literal["PRESENT", "ABSENT", "HYPOTHETICAL", "FAMILY", "POSSIBLE"]

_pipeline = None
_model_name = "cross-encoder/nli-MiniLM2-L6-H768"  # Lightweight NLI for CPU


def _get_pipeline():
    """Lazy-load the zero-shot classification pipeline."""
    global _pipeline
    if _pipeline is None:
        try:
            from transformers import pipeline  # type: ignore
            logger.info("Loading zero-shot NLI pipeline: %s", _model_name)
            _pipeline = pipeline(
                "zero-shot-classification",
                model=_model_name,
                device=-1,   # CPU; set to 0 for GPU
            )
            logger.info("NLI pipeline loaded.")
        except ImportError:
            logger.warning("transformers not installed — BioBERT variant unavailable.")
            return None
        except Exception as exc:
            logger.warning("Failed to load NLI model: %s — falling back to NegEx.", exc)
            return None
    return _pipeline


# Hypothesis templates for zero-shot NLI
HYPOTHESIS_TEMPLATES = {
    "PRESENT": "The patient currently has {}.",
    "ABSENT": "The patient does not have {} and it was explicitly denied or ruled out.",
    "HYPOTHETICAL": "Whether the patient has {} is uncertain or hypothetical.",
    "FAMILY": "A family member of the patient has {}.",
    "POSSIBLE": "The patient possibly or probably has {}.",
}


def classify(text: str, entity_term: str, sentence_context: str = "") -> dict:
    """Classify assertion type using zero-shot NLI.

    Falls back to heuristic regex if the NLI model is unavailable.

    Args:
        text: Full transcription text.
        entity_term: The clinical entity term to classify.
        sentence_context: The sentence containing the entity (for better context).

    Returns:
        dict with negated (bool), context (str), confidence (float), assertion_type (str).
    """
    pipe = _get_pipeline()

    # Graceful fallback to NegEx-style heuristic if model unavailable
    if pipe is None:
        from app.nlp.variants.negex_v1 import classify as negex_classify
        # Approximate entity position for NegEx fallback
        text_lower = text.lower()
        term_lower = entity_term.lower()
        idx = text_lower.find(term_lower)
        if idx == -1:
            return {"negated": False, "context": "patient", "confidence": 0.7,
                    "assertion_type": "PRESENT", "fallback": True}
        return {**negex_classify(text_lower, idx, idx + len(term_lower)),
                "assertion_type": "PRESENT", "fallback": True}

    # Use the sentence containing the entity for better NLI context
    context = sentence_context or text[:500]  # Limit to 500 chars for speed

    labels = list(HYPOTHESIS_TEMPLATES.keys())
    hypotheses = [HYPOTHESIS_TEMPLATES[l].format(entity_term) for l in labels]

    try:
        result = pipe(
            context,
            candidate_labels=labels,
            hypothesis_template="{}",
            multi_label=False,
        )
    except Exception as exc:
        logger.warning("NLI classification failed for '%s': %s", entity_term, exc)
        return {"negated": False, "context": "patient", "confidence": 0.6,
                "assertion_type": "PRESENT", "fallback": True}

    top_label: str = result["labels"][0]
    top_score: float = result["scores"][0]

    # Map assertion type to OmniMatch schema
    assertion_map = {
        "PRESENT": {"negated": False, "context": "patient"},
        "ABSENT": {"negated": True, "context": "patient"},
        "HYPOTHETICAL": {"negated": False, "context": "hypothetical"},
        "FAMILY": {"negated": False, "context": "family"},
        "POSSIBLE": {"negated": False, "context": "hypothetical"},
    }
    mapping = assertion_map.get(top_label, {"negated": False, "context": "patient"})

    return {
        **mapping,
        "confidence": round(top_score, 3),
        "assertion_type": top_label,
        "fallback": False,
    }


def is_available() -> bool:
    """Check if the BioBERT variant is available in this environment."""
    try:
        import transformers  # noqa: F401
        return True
    except ImportError:
        return False
