"""Offline, dependency-free regression evaluation. This script never trains a model."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from app.nlp.negex_pipeline import extract_entities

ROOT = Path(__file__).resolve().parent


def evaluate(dataset: Path) -> dict:
    raw = dataset.read_bytes()
    data = json.loads(raw)
    cases = list(data["additional_cases"])
    for term in data["terms"]:
        for template in data["templates"]:
            cases.append({"text": template["text"].format(term=term), "expected": [
                {"term": term, "context": template["context"], "negated": template["negated"]}
            ]})
    failures = []
    correct = total = 0
    groups = {}
    for case in cases:
        entities = extract_entities(case["text"])
        for expected in case["expected"]:
            total += 1
            relevant = [e for e in entities if e["term"] == expected["term"]]
            passed = any(e["context"] == expected["context"] and e["negated"] == expected["negated"] for e in relevant)
            correct += int(passed)
            label = "negated" if expected["negated"] else expected["context"]
            group = groups.setdefault(label, {"correct": 0, "total": 0})
            group["correct"] += int(passed)
            group["total"] += 1
            if not passed:
                failures.append({"text": case["text"], "expected": expected, "actual_for_term": relevant})
    return {
        "dataset_version": data["version"], "dataset_sha256": hashlib.sha256(raw).hexdigest(),
        "rules_sha256": hashlib.sha256((ROOT / "app/nlp/negex_pipeline.py").read_bytes()).hexdigest(),
        "provenance": data["provenance"], "case_count": len(cases),
        "metric": "Expected target term present with the expected context and negation",
        "correct": correct, "total": total, "target_assertion_accuracy": correct / total,
        "by_context": groups, "failures": failures,
        "limits": "Synthetic regression checks on known vocabulary. Does not measure all extracted false positives, NER F1, speech accuracy, retrieval relevance or clinical validity. No weights are trained or fine-tuned."
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=ROOT / "evaluation/context_cases.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = evaluate(args.dataset)
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered)
    return int(bool(report["failures"]))


if __name__ == "__main__":
    raise SystemExit(main())
