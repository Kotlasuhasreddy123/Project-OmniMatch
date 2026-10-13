"""
Qdrant collection configuration — optimal index settings based on literature.

Research basis (Qdrant docs + benchmarks):
  - Cosine distance optimal for normalized sentence embeddings
  - HNSW index: m=16 (connections per layer), ef_construct=100 (build quality)
    → Achieves 95% recall at 10x speed vs. brute-force on 10k+ vectors
  - on_disk_payload=True: keeps vector payload on disk, vectors in RAM
    → Reduces RAM usage by ~60% on large collections
  - Quantization (scalar int8): ~4x RAM reduction, <5% accuracy loss
    → Use on Free Tier EC2 t2.micro (1GB RAM constraint)

Collection size estimate for OmniMatch:
  - 500 RECRUITING trials × 384 floats × 4 bytes = ~768KB RAM (no quantization)
  - With int8 quantization: ~192KB — trivially fits in Free Tier
"""

from __future__ import annotations

from qdrant_client.http.models import (
    Distance,
    HnswConfigDiff,
    OptimizersConfigDiff,
    QuantizationConfig,
    ScalarQuantization,
    ScalarQuantizationConfig,
    ScalarType,
    VectorParams,
)

# ---------------------------------------------------------------------------
# Optimal collection configuration
# ---------------------------------------------------------------------------

VECTOR_SIZE = 384   # all-MiniLM-L6-v2 output dimension

OPTIMIZED_VECTORS_CONFIG = VectorParams(
    size=VECTOR_SIZE,
    distance=Distance.COSINE,
    hnsw_config=HnswConfigDiff(
        m=16,               # Number of edges per node (higher = better recall, more RAM)
        ef_construct=100,   # Build-time search width (higher = better index quality)
        full_scan_threshold=10_000,  # Use HNSW above this count
    ),
    on_disk=False,          # Keep vectors in RAM for speed (small collection)
)

QUANTIZED_VECTORS_CONFIG = VectorParams(
    size=VECTOR_SIZE,
    distance=Distance.COSINE,
    hnsw_config=HnswConfigDiff(m=16, ef_construct=100),
    quantization_config=QuantizationConfig(
        scalar=ScalarQuantization(
            scalar=ScalarQuantizationConfig(
                type=ScalarType.INT8,
                quantile=0.99,       # Preserve 99th percentile precision
                always_ram=True,     # Keep quantized vectors in RAM
            )
        )
    ),
    on_disk=True,           # Payload to disk — saves RAM on Free Tier
)

OPTIMIZERS_CONFIG = OptimizersConfigDiff(
    deleted_threshold=0.2,          # Rebuild index when 20% vectors deleted
    vacuum_min_vector_number=1000,  # Don't vacuum tiny collections
    default_segment_number=2,       # Parallel segment processing
    max_optimization_threads=1,     # Conservative for t2.micro (1 vCPU)
    memmap_threshold=50_000,        # Use memory-mapped files above this count
    indexing_threshold=20_000,      # Build HNSW index above this count
    flush_interval_sec=5,           # Flush WAL every 5 seconds
)


def get_collection_config(use_quantization: bool = False) -> dict:
    """Return the optimal Qdrant collection configuration.

    Args:
        use_quantization: If True, use int8 quantization (for Free Tier/low RAM).
                          If False, use full float32 (for accuracy).

    Returns:
        Dict of kwargs for qdrant_client.create_collection().
    """
    vectors_config = QUANTIZED_VECTORS_CONFIG if use_quantization else OPTIMIZED_VECTORS_CONFIG
    return {
        "vectors_config": vectors_config,
        "optimizers_config": OPTIMIZERS_CONFIG,
        "shard_number": 1,          # Single shard for small deployment
        "replication_factor": 1,    # No replication for Free Tier
    }
