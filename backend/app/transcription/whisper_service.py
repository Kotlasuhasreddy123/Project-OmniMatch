"""Whisper ASR service — transcribes audio from in-memory buffers only.

SECURITY: Audio bytes MUST be passed as io.BytesIO — never written to disk.
"""

from __future__ import annotations

import io
import logging
import subprocess
import time
from functools import lru_cache

import numpy as np

logger = logging.getLogger(__name__)

# Lazy import to avoid loading Whisper at module import time
_whisper_module = None
_model = None


def _get_whisper():
    """Lazy-load the whisper module."""
    global _whisper_module
    if _whisper_module is None:
        import whisper  # type: ignore
        _whisper_module = whisper
    return _whisper_module


def get_whisper_model(model_name: str = "base"):
    """Load and cache the Whisper model.

    Args:
        model_name: Whisper model size (tiny/base/small/medium/large).

    Returns:
        Loaded Whisper model instance.
    """
    global _model
    if _model is None:
        whisper = _get_whisper()
        logger.info("Loading Whisper model: %s", model_name)
        _model = whisper.load_model(model_name)
        logger.info("Whisper model loaded.")
    return _model


class TranscriptionService:
    """Wraps OpenAI Whisper for RAM-only audio transcription."""

    def __init__(self, model_name: str = "base") -> None:
        self.model_name = model_name

    def transcribe_buffer(self, audio_buffer: io.BytesIO) -> dict:
        """Transcribe audio from an in-memory buffer.

        The buffer is read, converted to a numpy float32 array, and passed
        directly to Whisper. No temporary files are created.

        Args:
            audio_buffer: In-memory audio bytes (WAV or WebM format).

        Returns:
            dict with keys: transcription, duration_seconds, language.
        """
        start = time.perf_counter()

        model = get_whisper_model(self.model_name)

        # Read raw bytes and decode via soundfile (in-memory)
        audio_buffer.seek(0)
        raw_bytes = audio_buffer.read()

        # Browser MediaRecorder commonly sends WebM/Opus. FFmpeg decodes through
        # stdin/stdout only: no filename or temporary audio file is created.
        try:
            decoded = subprocess.run(
                ["ffmpeg", "-nostdin", "-loglevel", "error", "-i", "pipe:0",
                 "-f", "f32le", "-ac", "1", "-ar", "16000", "pipe:1"],
                input=raw_bytes, capture_output=True, check=True, timeout=120,
            )
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise ValueError("Audio decode failed; check FFmpeg and the recording format") from exc
        audio_numpy = np.frombuffer(decoded.stdout, dtype=np.float32).copy()
        if audio_numpy.size == 0:
            raise ValueError("Decoded audio is empty")

        # Transcribe — audio stays in RAM as numpy array
        result = model.transcribe(audio_numpy, fp16=False, word_timestamps=True)

        duration = time.perf_counter() - start

        # Extract word-level confidence scores (FEATURE 6: transcript heatmap)
        word_confidences = []
        for segment in result.get("segments", []):
            for word_info in segment.get("words", []):
                word_confidences.append({
                    "word": word_info.get("word", "").strip(),
                    "confidence": round(float(word_info.get("probability", 1.0)), 3),
                    "start_time": round(float(word_info.get("start", 0.0)), 2),
                })

        # Immediately release reference — let GC collect the audio array
        del audio_numpy
        del raw_bytes

        return {
            "transcription": result.get("text", "").strip(),
            "duration_seconds": round(duration, 3),
            "language": result.get("language", "en"),
            "word_confidences": word_confidences,
        }


# Module-level singleton
_transcription_service: TranscriptionService | None = None


def get_transcription_service(model_name: str = "base") -> TranscriptionService:
    """Return the singleton TranscriptionService instance.

    Args:
        model_name: Whisper model size.

    Returns:
        TranscriptionService singleton.
    """
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService(model_name)
    return _transcription_service
