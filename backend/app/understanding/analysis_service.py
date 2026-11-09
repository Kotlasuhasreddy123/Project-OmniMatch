"""Hybrid term proposals, assertion disagreement review, and separate text tone."""
import re
from app.nlp.negex_pipeline import extract_entities, _get_compiled_patterns, _check_context, subject_prefix
from .model_registry import MODELS

NER_TYPES = {'disease_disorder': 'DISEASE', 'sign_symptom': 'SYMPTOM',
             'medication': 'MEDICATION', 'diagnostic_procedure': 'PROCEDURE',
             'therapeutic_procedure': 'PROCEDURE', 'lab_value': 'LAB_VALUE'}


def span_context(text, start, end):
    lowered = text.lower()
    patterns = _get_compiled_patterns()
    beginning = max(lowered.rfind(mark, 0, start) for mark in '.!?') + 1
    prefix = subject_prefix(lowered, start)
    family = any(pattern.search(prefix) for pattern in patterns['family_context'])
    hypothetical = _check_context(lowered, start, end, patterns['hypothetical'])
    uncertain = _check_context(lowered, start, end, patterns['uncertainty_pre']) or _check_context(
        lowered, start, end, patterns['uncertainty_post'], look_before=False, look_after=True)
    negated = _check_context(lowered, start, end, patterns['pre_negation']) or _check_context(
        lowered, start, end, patterns['post_negation'], look_before=False, look_after=True)
    if re.search(r'\b(?:does|do|did)\s+not\s+deny\b', lowered[beginning:start]):
        negated = False
    if uncertain:
        negated = False
    return ('family' if family else 'hypothetical' if hypothetical or uncertain else 'patient'), bool(negated)


def analyze(text, runtime):
    entities = []
    for entity in extract_entities(text):
        matches = list(re.finditer(re.escape(entity['term']).replace(r'\ ', r'\s+'), text, re.I))
        matching = [match for match in matches if span_context(text, match.start(), match.end()) == (entity['context'], entity['negated'])]
        match = (matching or matches)[0] if matches else None
        entities.append({**entity, 'source': 'rules', 'start': match.start() if match else None, 'end': match.end() if match else None})
    for finding in runtime.ner(text):
        kind = NER_TYPES.get(finding['category'].lower())
        start, end = finding['start'], finding['end']
        if not kind or finding['score'] < .55 or not 0 <= start < end <= len(text):
            continue
        while start < end and text[start].isspace():
            start += 1
        while end > start and text[end-1].isspace():
            end -= 1
        if start == end:
            continue
        if any(entity['start'] is not None and max(entity['start'], start) < min(entity['end'], end) for entity in entities):
            continue
        context, negated = span_context(text, start, end)
        entities.append(dict(term=text[start:end].lower(), entity_type=kind, context=context, negated=negated,
                             confidence=finding['score'], status='pending', source='biomedical_transformer', start=start, end=end))
    # Every term stays pending. NLI can flag disagreement, never approve a term.
    reviews = []
    located = [entity for entity in entities if entity['start'] is not None]
    for entity in located[:12]:
        left = max(text.rfind(mark, 0, entity['start']) for mark in '.!?') + 1
        next_marks = [text.find(mark, entity['end']) for mark in '.!?']
        right = min((value+1 for value in next_marks if value >= 0), default=len(text))
        premise = text[max(left, entity['start']-450):min(right, entity['end']+450)].strip()
        scores = runtime.assertions(premise, entity['term'])
        ranked = sorted(scores, key=scores.get, reverse=True)
        top, second = ranked[:2]
        rule_label = 'family' if entity['context'] == 'family' else 'hypothetical' if entity['context'] == 'hypothetical' else 'negated' if entity['negated'] else 'patient'
        reviews.append(dict(term=entity['term'], start=entity['start'], rule_label=rule_label, nli_label=top,
                            entailment_scores=scores, disagreement=top != rule_label,
                            low_separation=scores[top]-scores[second] < .15))
    # Bound tone analysis explicitly; a general tone classifier is not a patient assessment.
    tone_text = text[:1600]
    tone_result = runtime.sentiment(tone_text)
    tone = tone_result['scores']
    ordered_tone = sorted(tone, key=tone.get, reverse=True)
    tone_label = ordered_tone[0] if tone[ordered_tone[0]] >= .6 and tone[ordered_tone[0]]-tone[ordered_tone[1]] >= .15 else 'unclear'
    return dict(entities=entities, assertion_reviews=reviews,
                assertion_reviewed_count=len(reviews), assertion_unreviewed_count=len(located)-len(reviews),
                sentiment={'scores': tone, 'label': tone_label, 'input_characters': len(tone_text),
                           'partial': len(tone_text) < len(text) or tone_result['token_truncated'],
                           'meaning': 'General text tone only. Not patient emotion, diagnosis, urgency or trial eligibility.'},
                models={key: {'id': MODELS[key][0], 'revision': MODELS[key][1]} for key in ['ner', 'sentiment', 'assertion']},
                limits=['English medical extraction; model scores are uncalibrated.',
                        'Only the first 12 located terms receive NLI review; tone is limited to the first 1600 characters and 256 tokens.',
                        'No term is automatically approved; tone does not affect trial matching.'])
