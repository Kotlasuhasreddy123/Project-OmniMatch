"""BM25 + dense RRF retrieval, cross-encoder reranking and quote-verified RAG.

Generated text is accepted only when it reproduces a whole retrieved passage.
Otherwise the response explicitly falls back to cited excerpts. No diagnosis,
eligibility confirmation, forecasting or prescription is generated.
"""
import hashlib
import math
import re
from collections import Counter
from .model_registry import MODELS
from app.security.model_policy import instruction_like
from app.nlp.negex_pipeline import extract_entities

STOP_WORDS = set('the a an is are was were i my me am do does can could would should what which how of for in to and or with this that study trial patient'.split())


def tokens(text):
    return [word for word in re.findall(r'\b\w+\b', text.lower()) if word not in STOP_WORDS]


def passages_from_trials(trials, limit=120):
    passages = []
    for trial in trials:
        identifier = trial.get('nct_id', '')
        if not re.fullmatch(r'(?:NCT\d{8}|DEMO-[A-Z0-9-]{1,64})', identifier):
            continue
        if not isinstance(trial.get('title', ''), str) or instruction_like(trial.get('title', '')):
            continue
        for field in ['title', 'brief_summary', 'eligibility_criteria']:
            raw = trial.get(field, '')
            if not isinstance(raw, str):
                continue
            if instruction_like(raw):
                continue
            section = 'record'
            offset = 0
            for line in raw.splitlines(keepends=True):
                if re.match(r'\s*inclusion\s*criteria\s*:\s*$', line, re.I):
                    section = 'inclusion'
                    offset += len(line)
                    continue
                if re.match(r'\s*exclusion\s*criteria\s*:\s*$', line, re.I):
                    section = 'exclusion'
                    offset += len(line)
                    continue
                leading = len(line)-len(line.lstrip())
                content = line.strip()
                for start in range(0, len(content), 400):
                    quote = content[start:start+480]
                    if not quote:
                        continue
                    left = offset+leading+start
                    passages.append(dict(nct_id=identifier, title=trial.get('title', ''), field=field,
                                         section=section, start=left, end=left+len(quote), quote=quote,
                                         quote_sha256=hashlib.sha256(quote.encode()).hexdigest()))
                offset += len(line)
    return passages[:limit], len(passages) > limit


def bm25(query, passages):
    terms = tokens(query)
    documents = [tokens(passage['quote']) for passage in passages]
    average = sum(map(len, documents))/max(1, len(documents)) or 1
    frequencies = Counter(word for document in documents for word in set(document))
    scores = []
    for document in documents:
        counts = Counter(document)
        score = 0.
        for term in set(terms):
            frequency = counts[term]
            inverse = math.log(1+(len(documents)-frequencies[term]+.5)/(frequencies[term]+.5))
            score += inverse * frequency * 2.5/(frequency+1.5*(.25+.75*len(document)/average))
        scores.append(score)
    return scores


def normalized(text):
    # Formatting-only normalization; do not strip minus signs or clinical words.
    text = re.sub(r'^[*•]\s+', '', text.strip().strip('"'))
    return ' '.join(text.split()).casefold()


def answer(question, approved_terms, trials, runtime):
    scope = {'retrieved_studies': len(trials), 'passage_limit': 120, 'entire_registry_searched': False}
    if instruction_like(question):
        return dict(answer='This request needs a staff review. Ask a question about study records without instructions to bypass safeguards.',
                    sources=[], abstained=True, generation_mode='security_review_required', generator_used=False, scope=scope)
    if re.search(r'\b(?:prescrib\w*|diagnos\w*|predict\w*)\b|\bwill\s+i\s+(?:get|develop)\b|\bwhat\s+(?:medicine|drug)\s+should\b', question, re.I):
        return dict(answer='Ask about study records and their requirements. This assistant does not diagnose, forecast disease or prescribe treatment.',
                    sources=[], abstained=True, generation_mode='out_of_scope', generator_used=False, scope=scope)
    passages, partial = passages_from_trials(trials)
    scope.update(passages_considered=len(passages), passages_truncated=partial)
    if not passages:
        return dict(answer='No indexed study evidence was available for the approved terms.', sources=[], abstained=True,
                    generation_mode='no_evidence', generator_used=False, scope=scope)
    query = question + ' Approved visit terms: ' + ', '.join(approved_terms)
    def ranking_text(item):
        section = item['section'] + ' criteria' if item['section'] in ['inclusion', 'exclusion'] else 'study information'
        # Typed literal mentions give a general web reranker clinical context
        # without inventing synonyms, facts or answers. Returned quotations and
        # offsets always refer to the original, unmodified study passage.
        terms = extract_entities(item['quote'])
        typed = '; '.join(f"{entity['entity_type'].lower()}: {entity['term']}" for entity in terms[:12])
        return f"{item['title']}\n{section}: {item['quote']}\nLiteral clinical terms: {typed}"
    vectors = runtime.embeddings([query] + [ranking_text(item) for item in passages])
    dense = [sum(a*b for a, b in zip(vectors[0], vector)) for vector in vectors[1:]]
    lexical = bm25(question, passages)
    dense_order = sorted(range(len(passages)), key=lambda index: dense[index], reverse=True)
    lexical_order = sorted(range(len(passages)), key=lambda index: lexical[index], reverse=True)
    fused = Counter()
    for ranking in [dense_order, lexical_order]:
        for rank, index in enumerate(ranking):
            fused[index] += 1/(60+rank+1)
    candidates = sorted(fused, key=fused.get, reverse=True)[:12]
    scores = runtime.rerank(question, [ranking_text(passages[index]) for index in candidates])
    if len(scores) != len(candidates):
        raise ValueError('Reranker returned an unexpected number of scores')
    ranked = sorted(zip(candidates, scores), key=lambda pair: pair[1], reverse=True)
    # Fixed heuristic relevance gate; raw logits are not probabilities or accuracy.
    if not ranked or ranked[0][1] <= 0:
        return dict(answer='I could not find sufficiently relevant evidence in the retrieved study fields. Try a specific study question or review the registry directly.',
                    sources=[], abstained=True, generation_mode='low_relevance', generator_used=False, scope=scope)
    selected = [dict(passages[index], source_id=f'S{rank+1}', rerank_score=float(score))
                for rank, (index, score) in enumerate(ranked[:3]) if score > 0]
    # Small bounded source passages keep source labels and question within T5's window.
    generation_sources = selected[:2]
    prompt = ('Select one complete passage that answers the question. Copy it exactly. Do not add facts.\n'
              + '\n'.join(f"{item['source_id']}: {item['quote']}" for item in generation_sources)
              + '\nQuestion: ' + question + '\nPassage:')
    draft = runtime.generate(prompt)
    generated = draft['text'] if isinstance(draft, dict) else draft
    accepted = next((item for item in generation_sources if normalized(generated) == normalized(item['quote'])), None)
    used = [accepted] if accepted else selected
    rendered = '\n'.join(f"{item['quote']} [{item['source_id']}]" for item in used)
    return dict(answer='Study record excerpts for review:\n' + rendered, sources=used, abstained=False,
                generation_mode='generated_quote_verified' if accepted else 'extractive_grounding_fallback',
                generator_used=True, scope=scope,
                generation_prompt_truncated=draft.get('prompt_truncated', False) if isinstance(draft, dict) else False,
                models={key: {'id': MODELS[key][0], 'revision': MODELS[key][1]} for key in ['embedding', 'reranker', 'generator']},
                limits=['Only retrieved study fields are searched; no enrollment or eligibility decision is made.',
                        'Sentiment never affects retrieval, eligibility or ranking.',
                        'Generated paraphrases are rejected; fallback excerpts preserve the source wording.'])
