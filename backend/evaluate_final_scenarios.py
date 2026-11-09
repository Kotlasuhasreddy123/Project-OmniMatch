"""Evaluate new synthetic development scenarios without fitting weights."""
import hashlib
import json
from pathlib import Path
from app.nlp.negex_pipeline import extract_entities

ROOT = Path(__file__).resolve().parent


def evaluate():
    path = ROOT/'evaluation/final_scenario_cases.json'
    data = json.loads(path.read_bytes())
    results = []
    for row in data['cases']:
        expected = {(item['term'], item['context'], item['negated']) for item in row['expected']}
        actual = {(item['term'], item['context'], item['negated']) for item in extract_entities(row['text'])}
        results.append(dict(id=row['id'], correct=expected == actual,
                            missing=sorted(expected-actual), extra=sorted(actual-expected)))
    return dict(provenance=data['provenance'], dataset_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                correct=sum(row['correct'] for row in results), total=len(results),
                metric='Exact term/context/negation SET agreement per synthetic note; includes extra entities.',
                cases=results)


if __name__ == '__main__':
    print(json.dumps(evaluate(), indent=2))
