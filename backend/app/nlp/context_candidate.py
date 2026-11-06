"""Experimental assertion classifier. Not used by the live extraction endpoint.

The model requires a known entity span; it does not discover medical entities.
Weights are plain JSON, not executable pickle files. Scores are uncalibrated.
"""
from __future__ import annotations
import json
import math
import re
from collections import Counter
from pathlib import Path


def context_features(text: str, start: int, end: int) -> str:
    if not 0 <= start < end <= len(text):
        raise ValueError('Entity span is outside the text')
    left = re.split(r'[.!?;]', text[:start].lower())[-1]
    right = re.split(r'[.!?;]', text[end:].lower())[0]
    before = re.findall(r'\b\w\w+\b', left)[-12:]
    after = re.findall(r'\b\w\w+\b', right)[:12]
    # Hide the entity's identity so the classifier learns contextual cues.
    return ' '.join(['l_' + word for word in before] + ['target'] + ['r_' + word for word in after])


class ContextCandidate:
    def __init__(self, artifact: Path):
        self.model = json.loads(artifact.read_text(encoding='utf-8'))
        if self.model.get('format') != 'omnimatch-context-tfidf-logistic-v1':
            raise ValueError('Unsupported model format')

    def predict(self, text: str, start: int, end: int) -> dict:
        tokens = re.findall(r'(?u)\b\w\w+\b', context_features(text, start, end))
        counts = Counter(tokens + [' '.join(pair) for pair in zip(tokens, tokens[1:])])
        vocabulary = self.model['vocabulary']
        values = {vocabulary[word]: count * self.model['idf'][vocabulary[word]]
                  for word, count in counts.items() if word in vocabulary}
        norm = math.sqrt(sum(value * value for value in values.values())) or 1
        scores = [intercept + sum(coef[index] * value / norm for index, value in values.items())
                  for coef, intercept in zip(self.model['coefficients'], self.model['intercepts'])]
        exp = [math.exp(score - max(scores)) for score in scores]
        probabilities = [value / sum(exp) for value in exp]
        best = max(range(len(scores)), key=scores.__getitem__)
        return {'label': self.model['classes'][best], 'uncalibrated_score': probabilities[best],
                'experimental': True}
