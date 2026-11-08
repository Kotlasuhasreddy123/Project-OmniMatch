"""Authenticated, opt-in local text understanding and source-grounded research."""
import asyncio
from functools import partial
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from starlette.concurrency import run_in_threadpool
from app.auth.jwt_handler import require_role
from app.config import settings
from app.models.schemas import ClinicalEntity, EntityStatus, UserRole
from app.trials.qdrant_service import get_qdrant_service
from .model_registry import MODELS
from .runtime import get_runtime, ModelUnavailable
from .analysis_service import analyze
from .rag_service import answer

router = APIRouter(prefix='/api/v1/understanding', tags=['Advanced text and evidence'],
                   dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.CLINICAL_STAFF]))])
_busy = asyncio.Lock()


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=12000)
    synthetic_only: Literal[True]

    @field_validator('text')
    @classmethod
    def not_blank(cls, value):
        if not value.strip():
            raise ValueError('Enter a fictional note')
        return value


class EvidenceRequest(BaseModel):
    question: str = Field(min_length=3, max_length=400)
    approved_entities: list[ClinicalEntity] = Field(min_length=1, max_length=100)
    synthetic_only: Literal[True]


def require_enabled():
    if not settings.advanced_nlp_enabled:
        raise HTTPException(503, 'Advanced local models are disabled. Follow docs/ADVANCED_NLP_AND_RAG.md to enable and prepare them.')


async def compute(function):
    if _busy.locked():
        raise HTTPException(429, 'Another local model analysis is running. Please wait for it to finish.')
    async with _busy:
        try:
            return await run_in_threadpool(function)
        except ModelUnavailable as exc:
            raise HTTPException(503, str(exc)) from exc


@router.get('/status')
async def model_status():
    from importlib.util import find_spec
    dependencies_ready = all(find_spec(module) is not None for module in ['torch', 'transformers', 'sentencepiece'])
    models = []
    for name, (repo, revision) in MODELS.items():
        ready = False
        try:
            from huggingface_hub import try_to_load_from_cache
            from pathlib import Path
            paths = [try_to_load_from_cache(repo, filename, revision=revision) for filename in ['model.safetensors', 'config.json', 'tokenizer_config.json']]
            ready = all(isinstance(path, str) and Path(path).is_file() for path in paths)
        except ImportError:
            pass
        models.append({'task': name, 'id': repo, 'revision': revision, 'cached': ready})
    return {'enabled': settings.advanced_nlp_enabled, 'local_only': True, 'models': models, 'dependencies_ready': dependencies_ready,
            'validated_medical_accuracy_98': False}


@router.post('/analyze')
async def analyze_note(body: AnalyzeRequest):
    require_enabled()
    return await compute(partial(analyze, body.text, get_runtime()))


@router.post('/answer')
async def answer_study_question(body: EvidenceRequest):
    require_enabled()
    approved = [entity.term for entity in body.approved_entities if entity.status == EntityStatus.APPROVED
                and entity.context == 'patient' and not entity.negated]
    if not approved:
        raise HTTPException(400, 'Approve at least one affirmed patient term before searching study evidence.')
    try:
        trials = await get_qdrant_service().search(approved, top_k=20)
    except Exception as exc:
        raise HTTPException(503, 'The local trial index is unavailable. Start Qdrant and the backend, then try again.') from exc
    return await compute(partial(answer, body.question, approved, trials, get_runtime()))
