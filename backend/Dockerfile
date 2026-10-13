# OmniMatch Backend — FastAPI + Whisper + NLP
# Multi-stage build — CPU-only torch for AWS Free Tier

# ---------------------------------------------------------------------------
# Stage 1: builder
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# System dependencies for audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libsndfile1 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Ensure pip, setuptools, wheel are all current BEFORE any package installs
# This fixes the `No module named pkg_resources` error with openai-whisper
RUN pip install --upgrade pip setuptools wheel

# Install Python deps — split into two steps so torch (large) caches separately
COPY requirements.txt .

# Step 1: Install torch CPU separately (large file, ~190MB)
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    "torch==2.3.1+cpu"

# Step 2: Install openai-whisper after torch is in place
RUN pip install --no-cache-dir "openai-whisper==20231117"

# Step 3: Install all other requirements
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download spaCy model
RUN python -m spacy download en_core_web_sm

# ---------------------------------------------------------------------------
# Stage 2: runtime
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

WORKDIR /app

# Runtime system libs only
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder's system python (not a venv)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY app/ ./app/

ENV PYTHONPATH="/app"

# Create data directory for SQLite
RUN mkdir -p /app/data

# Non-root user
RUN useradd --no-create-home --shell /bin/false omniuser && \
    chown -R omniuser:omniuser /app
USER omniuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
