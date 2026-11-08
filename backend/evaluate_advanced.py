"""Real, pinned-checkpoint synthetic development evaluation; no fitting or mocks.

Models must already be cached. This is not a representative clinical test set.
RAG is evaluated against three fixed fictional studies, not a running Qdrant.
"""
import argparse
import hashlib
import json
import platform
import time
from pathlib import Path
from app.nlp.negex_pipeline import extract_entities
from app.understanding.analysis_service import analyze
from app.understanding.rag_service import answer
from app.understanding.runtime import LocalTransformers
from app.understanding.model_registry import MODELS

ROOT = Path(__file__).resolve().parent


def summary(outcomes):
    return {'correct': sum(outcomes), 'total': len(outcomes), 'fraction': sum(outcomes)/len(outcomes) if outcomes else None}


def run(output):
    import torch, transformers
    fixtures_path = ROOT/'evaluation/advanced_cases.json'
    fixtures = json.loads(fixtures_path.read_bytes())
    trials = json.loads((ROOT/'app/data/demo_trials.json').read_bytes())
    runtime = LocalTransformers(local_only=True)
    report = {'provenance': fixtures['provenance'], 'models': {key: {'id': value[0], 'revision': value[1]} for key, value in MODELS.items()},
              'fixtures_sha256': hashlib.sha256(fixtures_path.read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
              'service_sha256': {name: hashlib.sha256((ROOT/'app/understanding'/name).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
                                 for name in ['runtime.py', 'analysis_service.py', 'rag_service.py', 'model_registry.py']},
              'python': platform.python_version(), 'torch': torch.__version__, 'transformers': transformers.__version__,
              'device': 'cpu', 'threads': 4, 'fine_tuned_here': False, 'overall_medical_accuracy_98_validated': False}
    started = time.perf_counter()
    nlp_rows, rules_ok, hybrid_ok = [], [], []
    for case in fixtures['ner']:
        print('NER:', case['text'][:65], flush=True)
        before = extract_entities(case['text'])
        result = analyze(case['text'], runtime)
        for expected in case['expected']:
            check = lambda values: any(' '.join(item['term'].lower().split()) == expected['term'].lower()
                                       and item['context'] == expected['context'] and item['negated'] == expected['negated'] for item in values)
            a, b = check(before), check(result['entities'])
            rules_ok.append(a); hybrid_ok.append(b)
            nlp_rows.append({'text': case['text'], 'expected': expected, 'rule_target_found': a, 'hybrid_target_found': b})
    report['target_term_context'] = {'rules': summary(rules_ok), 'hybrid': summary(hybrid_ok), 'cases': nlp_rows,
                                    'limits': 'Expected target presence only, not full NER precision/recall/F1. Sparse author-created English examples.'}
    assertion_rows = []
    for case in fixtures['assertion']:
        scores = runtime.assertions(case['text'], case['term'])
        predicted = max(scores, key=scores.get)
        assertion_rows.append({**case, 'prediction': predicted, 'scores': scores, 'correct': predicted == case['label']})
    report['nli_assertion'] = {**summary([row['correct'] for row in assertion_rows]), 'cases': assertion_rows,
                               'limits': 'General SNLI/MultiNLI checkpoint; context suggestions only, never automatic clinical corrections.'}
    tone_rows = []
    for case in fixtures['sentiment']:
        tone = runtime.sentiment(case['text'])
        scores = tone['scores']; ranked = sorted(scores, key=scores.get, reverse=True)
        unclear = scores[ranked[0]] < .6 or scores[ranked[0]]-scores[ranked[1]] < .15
        tone_rows.append({**case, 'prediction': ranked[0], 'display_label': 'unclear' if unclear else ranked[0],
                          'scores': scores, 'correct': ranked[0] == case['label']})
    report['general_tone'] = {**summary([row['correct'] for row in tone_rows]), 'cases': tone_rows,
                              'unclear_count': sum(row['display_label'] == 'unclear' for row in tone_rows),
                              'limits': 'General wording labels, not patient emotion, psychiatric state or urgency; medical-negative wording can be confusing.'}
    rag_rows, citations_ok, expected_results = [], [], []
    for case in fixtures['rag']:
        print('RAG:', case['question'], flush=True)
        response = answer(case['question'], case['terms'], trials, runtime)
        if case.get('expect_abstain'):
            correct = response['abstained']
        else:
            correct = any(source['nct_id'] == case['expected_trial'] and case['expected_quote'].lower() in source['quote'].lower() for source in response['sources'])
        expected_results.append(correct)
        for source in response['sources']:
            trial = next(trial for trial in trials if trial['nct_id'] == source['nct_id'])
            quote = trial[source['field']][source['start']:source['end']]
            citations_ok.append(quote == source['quote'] and hashlib.sha256(quote.encode()).hexdigest() == source['quote_sha256'])
        rag_rows.append({**case, 'correct': correct, 'response': response})
    report['rag'] = {'expected_source_or_abstention': summary(expected_results), 'citation_integrity': summary(citations_ok),
                     'cases': rag_rows, 'limits': 'Fixed fictional corpus, expected source phrase or abstention only. Not clinical answer accuracy or registry-wide recall.'}
    report['elapsed_seconds_including_first_load'] = round(time.perf_counter()-started, 2)
    report['limitations'] = ['No training or parameter tuning used these cases.', 'This is development evidence, not independent clinical validation.',
                             'Neither pretrained models nor RAG establish universal 98% performance.', 'Docker/WorkOS/live registry integration is not exercised by this offline model harness.']
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({key: report[key] if key == 'elapsed_seconds_including_first_load' else {k: v for k, v in report[key].items() if k not in ['cases', 'limits']} for key in ['target_term_context', 'nli_assertion', 'general_tone', 'rag', 'elapsed_seconds_including_first_load']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT.parent/'docs/advanced-model-evaluation.json')
    run(parser.parse_args().output)
