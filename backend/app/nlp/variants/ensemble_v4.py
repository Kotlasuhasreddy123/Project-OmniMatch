"""
Variant 4: Ensemble Voter — Combines NegEx + NegBio + optional BioBERT.

Research basis:
  - Ensemble methods consistently outperform individual models in clinical NLP
    (He et al., 2020 i2b2 challenge winner used rule+ML ensemble).
  - NegBio+NegEx agreement increases confidence; disagreement triggers BioBERT.
  - Target: ≥97% negation recall (safety-critical: false negatives are dangerous).

Ensemble strategy:
  1. Run NegEx (fast, ~0.5ms)
  2. Run NegBio (medium, ~3ms)
  3. If both AGREE → use agreed result, boost confidence
  4. If they DISAGREE → run BioBERT as tiebreaker (if available), else use NegEx
  5. Local synthetic benchmark favors NegEx over this NegBio implementation.

Performance must be measured on held-out data; no accuracy is assumed here.
"""

from __future__ import annotations
import logging
from typing import Literal

logger = logging.getLogger(__name__)


def classify_ensemble(
    text: str,
    entity_term: str,
    entity_start: int,
    entity_end: int,
    use_biobert: bool = False,
) -> dict:
    """Ensemble negation classification combining NegEx + NegBio + optional BioBERT.

    Decision flow:
      1. Both agree → return agreed result (boosted confidence)
      2. Disagree, BioBERT available → use BioBERT as tiebreaker
      3. Disagree, no BioBERT → use NegEx (better on current local test set)

    Args:
        text: Full transcription text (lowercased).
        entity_term: The entity term string.
        entity_start: Character start position.
        entity_end: Character end position.
        use_biobert: Whether to attempt BioBERT tiebreaking.

    Returns:
        dict with negated, context, confidence, source (which variant decided),
        agreement (bool, whether NegEx+NegBio agreed).
    """
    from app.nlp.variants import negex_v1, negbio_v2

    # Step 1: Run NegEx
    negex_result = negex_v1.classify(text, entity_start, entity_end)

    # Step 2: Run NegBio
    negbio_result = negbio_v2.classify(text, entity_start, entity_end)

    negex_negated = negex_result["negated"]
    negbio_negated = negbio_result["negated"]
    negex_context = negex_result["context"]
    negbio_context = negbio_result["context"]

    # Agreement check
    negation_agrees = negex_negated == negbio_negated
    context_agrees = negex_context == negbio_context

    if negation_agrees and context_agrees:
        # Both agree — boost confidence by average + agreement bonus
        avg_conf = (negex_result["confidence"] + negbio_result["confidence"]) / 2
        boosted = min(0.99, avg_conf + 0.04)
        return {
            "negated": negbio_negated,
            "context": negbio_context,
            "confidence": round(boosted, 3),
            "source": "ensemble_agree",
            "agreement": True,
        }

    # Disagreement — try BioBERT if available
    if use_biobert:
        try:
            from app.nlp.variants import biobert_v3
            if biobert_v3.is_available():
                # Extract sentence context for BioBERT
                sentences = text.split(".")
                sentence_ctx = ""
                for s in sentences:
                    if entity_term.lower() in s.lower():
                        sentence_ctx = s.strip()
                        break

                bio_result = biobert_v3.classify(text, entity_term, sentence_ctx)
                if not bio_result.get("fallback"):
                    return {
                        "negated": bio_result["negated"],
                        "context": bio_result["context"],
                        "confidence": round(bio_result["confidence"] * 0.95, 3),  # slight penalty for tiebreak
                        "source": "biobert_tiebreak",
                        "agreement": False,
                    }
        except Exception as exc:
            logger.debug("BioBERT tiebreak failed: %s", exc)

    # Default tiebreak: prefer the locally stronger deterministic baseline.
    # Reduce confidence to reflect uncertainty
    reduced_conf = round(negex_result["confidence"] * 0.88, 3)
    return {
        "negated": negex_negated,
        "context": negex_context,
        "confidence": reduced_conf,
        "source": "negex_tiebreak",
        "agreement": False,
    }


def benchmark_variants(transcripts: list[dict]) -> dict:
    """Run all 4 variants on test transcripts and compute accuracy metrics.

    Args:
        transcripts: List of dicts with keys: transcript, expected_negated (list of terms).

    Returns:
        dict mapping variant name → {precision, recall, f1, avg_time_ms}.
    """
    import time
    from app.nlp.negex_pipeline import extract_entities

    results = {
        "negex_v1": {"tp": 0, "fp": 0, "fn": 0, "total_ms": 0},
        "negbio_v2": {"tp": 0, "fp": 0, "fn": 0, "total_ms": 0},
        "ensemble_v4": {"tp": 0, "fp": 0, "fn": 0, "total_ms": 0},
    }

    from app.nlp.variants import negex_v1, negbio_v2

    for t in transcripts:
        text = t["transcript"].lower()
        expected_neg = {e.lower() for e in t.get("expected_negated", [])}

        for variant_name in results:
            start = time.perf_counter()

            if variant_name == "negex_v1":
                # Use base pipeline but with NegEx classifier
                entities = extract_entities(text)
                detected_neg = {e["term"] for e in entities if e["negated"]}
            elif variant_name == "negbio_v2":
                entities = extract_entities(text)
                # Re-classify with NegBio
                detected_neg = set()
                for e in entities:
                    idx = text.find(e["term"])
                    if idx >= 0:
                        r = negbio_v2.classify(text, idx, idx + len(e["term"]))
                        if r["negated"]:
                            detected_neg.add(e["term"])
            else:  # ensemble
                entities = extract_entities(text)
                detected_neg = set()
                for e in entities:
                    idx = text.find(e["term"])
                    if idx >= 0:
                        r = classify_ensemble(text, e["term"], idx, idx + len(e["term"]))
                        if r["negated"]:
                            detected_neg.add(e["term"])

            elapsed_ms = (time.perf_counter() - start) * 1000
            results[variant_name]["total_ms"] += elapsed_ms

            # Compute TP/FP/FN (partial match: term substring counts)
            for neg_term in expected_neg:
                if any(neg_term in det or det in neg_term for det in detected_neg):
                    results[variant_name]["tp"] += 1
                else:
                    results[variant_name]["fn"] += 1
            for det in detected_neg:
                if not any(exp in det or det in exp for exp in expected_neg):
                    results[variant_name]["fp"] += 1

    # Compute final metrics
    metrics = {}
    n = max(1, len(transcripts))
    for name, r in results.items():
        tp, fp, fn = r["tp"], r["fp"], r["fn"]
        precision = tp / max(1, tp + fp)
        recall = tp / max(1, tp + fn)
        f1 = 2 * precision * recall / max(1e-9, precision + recall)
        metrics[name] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "avg_time_ms": round(r["total_ms"] / n, 2),
        }

    return metrics
