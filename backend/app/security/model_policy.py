"""Heuristic screening complements, but never replaces, permission/output gates."""
import re
import unicodedata

_INSTRUCTIONS = re.compile(
    r'ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions|'
    r'(?:reveal|print|expose)\s+(?:the\s+)?(?:system\s+prompt|api\s+key|secret)|'
    r'<\s*/?\s*(?:system|developer)\s*>|'
    r'\b(?:bypass|disable)\s+(?:consent|approval|security|guardrails)\b', re.I)


def instruction_like(text):
    value = unicodedata.normalize('NFKC', text)
    value = ''.join(char for char in value if unicodedata.category(char) != 'Cf')
    return bool(_INSTRUCTIONS.search(value))
