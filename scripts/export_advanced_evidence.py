"""Expose measured advanced-model development results with source freshness checks."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


if __name__ == '__main__':
    report = json.loads((ROOT/'docs/advanced-model-evaluation.json').read_text(encoding='utf-8'))
    for name, expected in report['service_sha256'].items():
        actual = hashlib.sha256((ROOT/'backend/app/understanding'/name).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
        if actual != expected:
            raise ValueError('Model evidence is stale for ' + name + '; rerun the real model evaluator')
    cases = report['rag']['cases']
    result = {
        'models': report['models'],
        'target_context_rules': report['target_term_context']['rules'],
        'target_context_hybrid': report['target_term_context']['hybrid'],
        'nli': {key: report['nli_assertion'][key] for key in ['correct', 'total', 'fraction']},
        'tone': {key: report['general_tone'][key] for key in ['correct', 'total', 'fraction', 'unclear_count']},
        'rag': report['rag']['expected_source_or_abstention'],
        'citations': report['rag']['citation_integrity'],
        'verified_generated_quotes': sum(case['response']['generation_mode'] == 'generated_quote_verified' for case in cases),
        'extractive_fallbacks': sum(case['response']['generation_mode'] == 'extractive_grounding_fallback' for case in cases),
        'overall_medical_98_validated': False,
    }
    path = ROOT/'frontend/src/data/advancedEvidence.json'
    path.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('Exported real-checkpoint development evidence; no clinical accuracy claim.')
