"""Qdrant vector database service for clinical trial embeddings."""

from __future__ import annotations

import logging
import uuid
import json
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from qdrant_client import AsyncQdrantClient
    from sentence_transformers import SentenceTransformer

from app.config import settings

logger = logging.getLogger(__name__)

VECTOR_SIZE = 384          # all-MiniLM-L6-v2 output dimension
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MATCH_SCORE_THRESHOLD = 0.65
DEMO_MATCH_SCORE_THRESHOLD = 0.40
TOP_K = 10

_qdrant_client: Any | None = None
_embedding_model: Any | None = None


def get_embedding_model() -> Any:
    """Load and return the singleton SentenceTransformer model.

    Returns:
        Loaded SentenceTransformer for generating 384-dim embeddings.
    """
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model: %s", EMBEDDING_MODEL)
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("Embedding model loaded.")
    return _embedding_model


def get_qdrant_client() -> Any:
    """Return the singleton AsyncQdrantClient.

    Returns:
        AsyncQdrantClient connected to the configured Qdrant instance.
    """
    global _qdrant_client
    if _qdrant_client is None:
        from qdrant_client import AsyncQdrantClient
        _qdrant_client = AsyncQdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            timeout=60,
        )
    return _qdrant_client


class QdrantService:
    """Manages the clinical_trials Qdrant collection and vector operations."""

    def __init__(self) -> None:
        self.collection = settings.qdrant_collection
        self.client = get_qdrant_client()

    async def ensure_collection(self) -> None:
        """Create the clinical_trials collection if it does not already exist."""
        existing = await self.client.get_collections()
        names = [c.name for c in existing.collections]
        if self.collection not in names:
            from qdrant_client.http.models import Distance, VectorParams
            await self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info("Created Qdrant collection: %s", self.collection)

    async def seed_demo_trials_if_empty(self) -> int:
        """Index clearly synthetic studies for a network-independent classroom demo."""
        if not settings.demo_mode:
            return 0
        await self.ensure_collection()
        count = await self.client.count(collection_name=self.collection, exact=True)
        if count.count:
            return 0
        data_path = Path(__file__).resolve().parents[1] / "data" / "demo_trials.json"
        trials = json.loads(data_path.read_text(encoding="utf-8"))
        for trial in trials:
            await self.upsert_trial(trial)
        logger.info("Indexed %d synthetic demonstration trials", len(trials))
        return len(trials)

    def _embed_trial(self, trial: dict) -> list[float]:
        """Generate an embedding vector for a trial's eligibility criteria + summary.

        Args:
            trial: Trial dict with eligibility_criteria, brief_summary, conditions.

        Returns:
            384-dimensional float list embedding.
        """
        text_parts = [
            trial.get("title", ""),
            trial.get("brief_summary", "")[:500],
            trial.get("eligibility_criteria", "")[:1000],
            " ".join(trial.get("conditions", [])),
        ]
        combined = " | ".join(p for p in text_parts if p)
        vector = get_embedding_model().encode(combined, normalize_embeddings=True)
        return vector.tolist()

    async def upsert_trial(self, trial: dict) -> None:
        """Insert or update a single trial in the Qdrant collection.

        Args:
            trial: Trial dict from ClinicalTrialsClient.
        """
        vector = self._embed_trial(trial)
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, trial["nct_id"]))

        from qdrant_client.http.models import PointStruct

        point = PointStruct(
            id=point_id,
            vector=vector,
            payload={
                "nct_id": trial["nct_id"],
                "title": trial["title"],
                "status": trial["status"],
                "phase": trial["phase"],
                "conditions": trial["conditions"],
                "brief_summary": trial["brief_summary"],
                "eligibility_criteria": trial["eligibility_criteria"],
                "sponsor": trial["sponsor"],
                "last_updated": trial["last_updated"],
                "locations": trial.get("locations", []),
            },
        )
        await self.client.upsert(collection_name=self.collection, points=[point])

    async def search(self, query_terms: list[str], top_k: int = TOP_K) -> list[dict]:
        """Search the Qdrant collection for trials matching the given clinical terms.

        Args:
            query_terms: List of approved entity terms from human verification.
            top_k: Maximum number of results to return.

        Returns:
            List of trial dicts with score and payload fields.
        """
        query_text = " ".join(query_terms)
        query_vector = get_embedding_model().encode(query_text, normalize_embeddings=True).tolist()

        results = await self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=top_k,
            score_threshold=DEMO_MATCH_SCORE_THRESHOLD if settings.demo_mode else MATCH_SCORE_THRESHOLD,
            with_payload=True,
        )

        return [
            {
                "nct_id": r.payload.get("nct_id", ""),
                "title": r.payload.get("title", ""),
                "score": round(r.score, 4),
                "phase": r.payload.get("phase", "N/A"),
                "status": r.payload.get("status", ""),
                "brief_summary": r.payload.get("brief_summary", ""),
                "conditions": r.payload.get("conditions", []),
                "sponsor": r.payload.get("sponsor", ""),
                "eligibility_criteria": r.payload.get("eligibility_criteria", ""),
                "last_updated": r.payload.get("last_updated", ""),
                "locations": r.payload.get("locations", []),
            }
            for r in results
        ]

    async def is_connected(self) -> bool:
        """Ping Qdrant to check connectivity.

        Returns:
            True if Qdrant is reachable, False otherwise.
        """
        try:
            await self.client.get_collections()
            return True
        except Exception:
            return False


_qdrant_service: QdrantService | None = None


def get_qdrant_service() -> QdrantService:
    """Return the singleton QdrantService instance."""
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantService()
    return _qdrant_service
