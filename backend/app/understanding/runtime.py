"""Lazy CPU-only transformer inference. Missing weights never become fake results."""
from __future__ import annotations
from functools import lru_cache
from collections import OrderedDict
import gc
from .model_registry import MODELS


class ModelUnavailable(RuntimeError):
    pass


class LocalTransformers:
    def __init__(self, local_only=True, max_models=2):
        if max_models < 1:
            raise ValueError('max_models must be positive')
        self.local_only = local_only
        self.max_models = max_models
        self.loaded = OrderedDict()

    def load(self, kind):
        if kind in self.loaded:
            self.loaded.move_to_end(kind)
            return self.loaded[kind]
        # The API serializes inference. Release the least recently used weights
        # before allocating another model on memory-limited laptops.
        while len(self.loaded) >= self.max_models:
            self.loaded.popitem(last=False)
            gc.collect()
        try:
            import torch
            from transformers import (AutoTokenizer, AutoModel, AutoModelForTokenClassification,
                                      AutoModelForSequenceClassification, AutoModelForSeq2SeqLM)
            torch.set_num_threads(4)
            repo, revision = MODELS[kind]
            options = dict(revision=revision, local_files_only=self.local_only, trust_remote_code=False)
            tokenizer = AutoTokenizer.from_pretrained(repo, use_fast=True, **options)
            cls = {'ner': AutoModelForTokenClassification, 'embedding': AutoModel,
                   'generator': AutoModelForSeq2SeqLM}.get(kind, AutoModelForSequenceClassification)
            model = cls.from_pretrained(repo, use_safetensors=True, **options).to('cpu').eval()
            self.loaded[kind] = (tokenizer, model)
            return tokenizer, model
        except Exception as exc:
            raise ModelUnavailable(f'Local {kind} model is unavailable. Install requirements-advanced.txt and run prepare_advanced_models.py.') from exc

    def ner(self, text):
        tokenizer, model = self.load('ner')
        import torch
        encoded = tokenizer(text, truncation=True, max_length=512, stride=64,
                            return_overflowing_tokens=True, return_offsets_mapping=True,
                            padding=True, return_tensors='pt')
        offsets = encoded.pop('offset_mapping').tolist()
        encoded.pop('overflow_to_sample_mapping', None)
        spans = []
        for row, mapping in enumerate(offsets):
            with torch.inference_mode():
                probabilities = model(**{key: value[row:row+1] for key, value in encoded.items()}).logits.softmax(-1)[0]
            scores, labels = probabilities.max(-1)
            current = None
            for (start, end), index, score in zip(mapping, labels.tolist(), scores.tolist()):
                label = model.config.id2label[index]
                if end <= start or label == 'O':
                    if current:
                        spans.append(current)
                        current = None
                    continue
                prefix, category = label.split('-', 1)
                if current and prefix == 'I' and current['category'] == category and start <= current['end'] + 2:
                    current['end'] = end
                    current['scores'].append(score)
                else:
                    if current:
                        spans.append(current)
                    current = dict(start=start, end=end, category=category, scores=[score])
            if current:
                spans.append(current)
        unique = {}
        for item in sorted(spans, key=lambda span: span['end']-span['start'], reverse=True):
            if any(other['category'] == item['category'] and other['start'] <= item['start'] and other['end'] >= item['end'] for other in unique.values()):
                continue
            unique[(item['start'], item['end'], item['category'])] = item
        return [dict(start=item['start'], end=item['end'], category=item['category'],
                     score=sum(item['scores'])/len(item['scores'])) for item in unique.values()]

    def sequence_scores(self, kind, texts, pairs=None):
        tokenizer, model = self.load(kind)
        import torch
        encoded = tokenizer(texts, text_pair=pairs, padding=True, truncation=True,
                            max_length=512 if kind == 'reranker' else 256, return_tensors='pt')
        with torch.inference_mode():
            logits = model(**encoded).logits
        return logits, model.config.id2label

    def sentiment(self, text):
        tokenizer, _ = self.load('sentiment')
        token_count = len(tokenizer(text, truncation=False)['input_ids'])
        logits, labels = self.sequence_scores('sentiment', [text])
        values = logits.softmax(-1)[0].tolist()
        return {'scores': {labels[index].lower(): float(value) for index, value in enumerate(values)},
                'token_truncated': token_count > 256}

    def assertions(self, premise, term):
        hypotheses = {
            'patient': f'The patient has {term}.',
            'negated': f'The patient does not have {term}.',
            'family': f'A family member, rather than the patient, has {term}.',
            'hypothetical': f'It is uncertain whether the patient has {term}.',
        }
        logits, labels = self.sequence_scores('assertion', [premise]*len(hypotheses), list(hypotheses.values()))
        entailment = next((index for index, label in labels.items() if label.lower() == 'entailment'), None)
        if entailment is None:
            raise ModelUnavailable('The pinned assertion checkpoint has an unexpected label mapping.')
        values = logits.softmax(-1)[:, entailment].tolist()
        # Independent entailment scores, not normalized medical probabilities.
        return dict(zip(hypotheses, map(float, values)))

    def embeddings(self, texts):
        tokenizer, model = self.load('embedding')
        import torch
        vectors = []
        for start in range(0, len(texts), 8):
            encoded = tokenizer(texts[start:start+8], padding=True, truncation=True, max_length=256, return_tensors='pt')
            with torch.inference_mode():
                hidden = model(**encoded).last_hidden_state
                mask = encoded['attention_mask'].unsqueeze(-1)
                pooled = (hidden*mask).sum(1)/mask.sum(1).clamp(min=1)
                vectors.extend(torch.nn.functional.normalize(pooled, dim=1).tolist())
        return vectors

    def rerank(self, question, passages):
        scores = []
        for start in range(0, len(passages), 4):
            batch = passages[start:start+4]
            logits, _ = self.sequence_scores('reranker', [question]*len(batch), batch)
            scores.extend(logits.flatten().tolist())
        return scores

    def generate(self, prompt):
        tokenizer, model = self.load('generator')
        import torch
        truncated = len(tokenizer(prompt, truncation=False)['input_ids']) > 512
        encoded = tokenizer(prompt, max_length=512, truncation=True, return_tensors='pt')
        with torch.inference_mode():
            output = model.generate(**encoded, do_sample=False, max_new_tokens=96, num_beams=1)
        return {'text': tokenizer.decode(output[0], skip_special_tokens=True), 'prompt_truncated': truncated}


@lru_cache(maxsize=1)
def get_runtime():
    return LocalTransformers(local_only=True)
