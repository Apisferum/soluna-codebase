"""
Shared runtime state for the audio services (Chord AI, Stem Separator,
Voice Separator).

This replaces the module-import side effects that used to live in
services/audio_api/main.py (model preloading, a background cleanup
thread, and in-process semaphores). Everything here is started and
stopped explicitly from the application lifespan instead of running
automatically whenever the module is imported.
"""

import logging
import threading
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI

logger = logging.getLogger("synestra.audio")

# In-memory registry of generated files awaiting download.
# Format: { id: {"paths": [...], "timestamp": float, ...} }
# In production this should move to Redis/DB-backed storage so it can be
# shared across multiple worker processes; for a single-worker deployment
# (see Dockerfile) in-memory state is fine.
separated_files: dict[str, dict[str, Any]] = {}

# Limit max concurrent heavy Demucs tasks (stem separation) to avoid OOM.
MAX_CONCURRENT_SEPARATION = 1
separation_semaphore = threading.Semaphore(MAX_CONCURRENT_SEPARATION)

# Limit max concurrent Chord AI (madmom/librosa) tasks to avoid CPU saturation.
MAX_CONCURRENT_CHORDS = 3
chord_semaphore = threading.Semaphore(MAX_CONCURRENT_CHORDS)

_CLEANUP_INTERVAL_SECONDS = 600  # 10 minutes
_FILE_TTL_SECONDS = 3600  # 1 hour

_cleanup_thread: threading.Thread | None = None
_cleanup_stop_event = threading.Event()


def register_files(entry_id: str, paths: list[str], **extra: Any) -> None:
    """Register generated files so they can be downloaded and later cleaned up."""
    separated_files[entry_id] = {
        "paths": paths,
        "timestamp": time.time(),
        **extra,
    }


def get_entry(entry_id: str) -> dict[str, Any] | None:
    return separated_files.get(entry_id)


def _cleanup_loop() -> None:
    """Background loop that deletes expired generated files."""
    while not _cleanup_stop_event.is_set():
        try:
            now = time.time()
            expired = [
                file_id
                for file_id, info in list(separated_files.items())
                if now - info.get("timestamp", 0) > _FILE_TTL_SECONDS
            ]

            for file_id in expired:
                info = separated_files.pop(file_id, {})
                for raw_path in info.get("paths", []):
                    try:
                        path = Path(raw_path)
                        if path.exists():
                            path.unlink()
                            logger.info("Deleted expired file: %s", path)
                    except Exception:
                        logger.exception("Error deleting expired file: %s", raw_path)
        except Exception:
            logger.exception("Error in audio cleanup loop")

        _cleanup_stop_event.wait(_CLEANUP_INTERVAL_SECONDS)


def _preload_models() -> None:
    """Warm the Demucs model caches so the first real request isn't slow."""
    try:
        from app.music.analysis import _get_separator, _get_separator_6stem

        _get_separator()
        _get_separator_6stem()
        logger.info("Audio models preloaded and ready")
    except Exception:
        logger.exception("Audio model preload failed; will load lazily on first request")


async def start_audio_runtime(app: FastAPI) -> None:
    """Call from the application lifespan on startup."""
    global _cleanup_thread

    _preload_models()

    _cleanup_stop_event.clear()
    _cleanup_thread = threading.Thread(target=_cleanup_loop, daemon=True)
    _cleanup_thread.start()
    logger.info("Audio cleanup thread started")


async def stop_audio_runtime(app: FastAPI) -> None:
    """Call from the application lifespan on shutdown."""
    _cleanup_stop_event.set()
