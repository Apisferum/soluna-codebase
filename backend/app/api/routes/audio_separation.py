import logging
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from app.core.config import settings
from app.music.analysis import STEM_TYPES, separate_audio_full, separate_audio_stems
from app.services.audio_runtime import get_entry, register_files, separation_semaphore

logger = logging.getLogger("synestra.audio")

router = APIRouter()

ALL_STEM_NAMES = ["vocals", "drums", "bass", "guitar", "piano", "other"]


def _validate_format(format: str) -> str:
    format = (format or "wav").lower().strip()
    if format not in {"wav", "mp3"}:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'wav' or 'mp3'.")
    return format


def _to_mp3(src: Path) -> Path:
    dst = src.with_suffix(".mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(src), "-codec:a", "libmp3lame", "-b:a", "192k", str(dst)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return dst


@router.post("/separate")
def separate_audio(file: UploadFile = File(...), format: str = Form("wav")):
    """Separate vocals and instrumental from an uploaded audio file.

    Args:
        file: Audio file upload
        format: Output container for stems: "wav" (default) or "mp3".
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File required")

    format = _validate_format(format)
    suffix = Path(file.filename).suffix or ".tmp"

    with separation_semaphore:
        with tempfile.NamedTemporaryFile(
            dir=settings.separated_dir, delete=False, suffix=suffix
        ) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)

        try:
            result = separate_audio_full(tmp_path)
            if not result:
                raise HTTPException(status_code=500, detail="Separation failed - model error")

            session_id = str(uuid.uuid4())
            vocals_path = Path(result["vocals"])
            instrumental_path = Path(result["instrumental"])

            if format == "mp3":
                try:
                    vocals_path = _to_mp3(vocals_path)
                    instrumental_path = _to_mp3(instrumental_path)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    logger.warning("MP3 conversion unavailable, falling back to WAV")
                    format = "wav"

            register_files(
                session_id,
                [str(vocals_path), str(instrumental_path)],
                vocals=str(vocals_path),
                instrumental=str(instrumental_path),
                format=format,
                type="separation",
            )

            return JSONResponse(
                {
                    "session_id": session_id,
                    "format": format,
                    "vocalsUrl": f"/api/separate/download/{session_id}/vocals?format={format}",
                    "instrumentalUrl": f"/api/separate/download/{session_id}/instrumental?format={format}",
                }
            )
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Separation error")
            raise HTTPException(status_code=500, detail=f"Separation failed: {exc}")
        finally:
            tmp_path.unlink(missing_ok=True)


@router.post("/separate-stems")
def separate_audio_6stems(file: UploadFile = File(...), format: str = Form("wav")):
    """Separate audio into 6 stems: vocals, drums, bass, guitar, piano, other.

    Uses the htdemucs_6s model. Processing takes 5-10 minutes for a
    3-minute song on CPU.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File required")

    format = _validate_format(format)
    suffix = Path(file.filename).suffix or ".tmp"

    with separation_semaphore:
        with tempfile.NamedTemporaryFile(
            dir=settings.separated_dir, delete=False, suffix=suffix
        ) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)

        try:
            result = separate_audio_stems(tmp_path)
            if not result:
                raise HTTPException(status_code=500, detail="6-stem separation failed - model error")

            session_id = str(uuid.uuid4())
            stem_data: dict[str, str] = {}
            all_paths: list[str] = []

            for stem_name, stem_path in result.items():
                stem_path = Path(stem_path)

                if format == "mp3":
                    try:
                        stem_path = _to_mp3(stem_path)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        logger.warning("MP3 conversion failed for %s, keeping WAV", stem_name)

                stem_data[stem_name] = str(stem_path)
                all_paths.append(str(stem_path))

            register_files(
                session_id,
                all_paths,
                **stem_data,
                format=format,
                type="6stem-separation",
            )

            stem_urls = {
                f"{stem_name}Url": f"/api/separate-stems/download/{session_id}/{stem_name}?format={format}"
                for stem_name in ALL_STEM_NAMES
                if stem_name in stem_data
            }

            return JSONResponse(
                {
                    "session_id": session_id,
                    "format": format,
                    "stems": list(stem_data.keys()),
                    **stem_urls,
                }
            )
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("6-stem separation error")
            raise HTTPException(status_code=500, detail=f"6-stem separation failed: {exc}")
        finally:
            tmp_path.unlink(missing_ok=True)


@router.get("/separate/download/{session_id}/{track_type}")
async def download_separated(session_id: str, track_type: str, format: str = "wav"):
    """Download a separated vocals/instrumental track."""
    entry = get_entry(session_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if track_type not in ("vocals", "instrumental"):
        raise HTTPException(status_code=400, detail="Invalid track type")

    if track_type not in entry:
        raise HTTPException(status_code=404, detail=f"Track '{track_type}' not found in this session")

    file_path = Path(entry[track_type])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File no longer available")

    ext = file_path.suffix.lower()
    media_type = "audio/mpeg" if ext == ".mp3" else "audio/wav"
    filename = f"{track_type}{ext or '.wav'}"

    return FileResponse(file_path, media_type=media_type, filename=filename)


@router.get("/separate-stems/download/{session_id}/{stem_type}")
async def download_stem(session_id: str, stem_type: str, format: str = "wav"):
    """Download a specific stem from 6-stem separation."""
    entry = get_entry(session_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if stem_type not in STEM_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid stem type. Must be one of: {', '.join(STEM_TYPES)}",
        )

    if stem_type not in entry:
        raise HTTPException(status_code=404, detail=f"Stem '{stem_type}' not found in this session")

    file_path = Path(entry[stem_type])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File no longer available")

    ext = file_path.suffix.lower()
    media_type = "audio/mpeg" if ext == ".mp3" else "audio/wav"
    filename = f"{stem_type}{ext or '.wav'}"

    return FileResponse(file_path, media_type=media_type, filename=filename)
