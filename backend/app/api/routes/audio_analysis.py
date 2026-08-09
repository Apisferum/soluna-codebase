import logging
import shutil
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from app.core.config import settings
from app.music.analysis import analyze_file
from app.music.youtube import (
    check_rate_limit,
    extract_audio,
    extract_video_id,
    get_remaining_requests,
    get_video_info,
)
from app.services.audio_runtime import (
    chord_semaphore,
    get_entry,
    register_files,
    separation_semaphore,
)

logger = logging.getLogger("synestra.audio")

router = APIRouter()

# madmom is an optional dependency (heavy, tricky to build on some
# platforms). Fall back to the librosa engine if it isn't installed.
try:
    from app.music.chord_madmom import (
        MADMOM_AVAILABLE,
        analyze_file_madmom,
    )

    if MADMOM_AVAILABLE:
        logger.info("madmom engine available - fast analysis enabled (~5-10s)")
    else:
        logger.info("madmom library not installed - using librosa engine (~1-3min)")
except ImportError:
    MADMOM_AVAILABLE = False

    def analyze_file_madmom(*args, **kwargs):  # type: ignore[no-redef]
        raise ImportError("madmom is not available")

    logger.info("madmom module not found - using librosa engine only")


def _run_analysis(audio_path: Path, *, separate_vocals: bool, use_madmom: bool) -> dict:
    """Pick the analysis engine and run it, mirroring the previous service's logic."""
    if not use_madmom:
        logger.info("Engine: LIBROSA (more accurate) | vocal filter: %s", separate_vocals)
        return analyze_file(audio_path, separate_vocals=separate_vocals)

    if separate_vocals:
        logger.info("Engine: LIBROSA (vocal filter enabled)")
        return analyze_file(audio_path, separate_vocals=True)

    if MADMOM_AVAILABLE:
        logger.info("Engine: MADMOM (fast) | vocal filter: off")
        return analyze_file_madmom(audio_path)

    logger.info("Engine: LIBROSA (fallback) | madmom not found")
    return analyze_file(audio_path, separate_vocals=False)


def _attach_instrumental_download(result: dict, entry_type: str) -> None:
    """If the analysis produced an instrumental track, register it for download."""
    if "instrumentalPath" not in result:
        return

    file_id = str(uuid.uuid4())
    path = result["instrumentalPath"]
    register_files(file_id, [path], type=entry_type)
    result["instrumentalUrl"] = f"/api/analyze/download/{file_id}/instrumental.wav"
    del result["instrumentalPath"]


@router.post("/analyze")
def analyze(
    file: UploadFile = File(...),
    separate_vocals: bool = Form(False),
    use_madmom: bool = Form(True),
):
    """Analyze an uploaded audio file for chords.

    Args:
        file: Audio file to analyze
        separate_vocals: If True, separate vocals before analysis for better
            accuracy (slower)
        use_madmom: If True, use the fast madmom engine. If False, use
            librosa (more detailed analysis)
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File required")

    active_semaphore = separation_semaphore if separate_vocals else chord_semaphore

    with active_semaphore:
        suffix = Path(file.filename).suffix or ".tmp"
        with tempfile.NamedTemporaryFile(
            dir=settings.separated_dir, delete=False, suffix=suffix
        ) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)

        try:
            result = _run_analysis(
                tmp_path,
                separate_vocals=separate_vocals,
                use_madmom=use_madmom,
            )
            _attach_instrumental_download(result, "analysis")
            return JSONResponse(result)
        except Exception:
            logger.exception("Analysis failed")
            raise HTTPException(status_code=500, detail="Analysis failed")
        finally:
            tmp_path.unlink(missing_ok=True)


@router.post("/analyze-youtube")
def analyze_youtube(
    url: str = Form(...),
    separate_vocals: bool = Form(False),
    use_madmom: bool = Form(True),
    client_ip: str = Form("unknown"),
):
    """Analyze a YouTube video for chords.

    Args:
        url: YouTube video URL
        separate_vocals: If True, separate vocals before analysis (slower,
            more accurate)
        use_madmom: If True, use the fast madmom engine. If False, use librosa.
        client_ip: Client IP for rate limiting
    """
    if not check_rate_limit(client_ip):
        remaining = get_remaining_requests(client_ip)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum 5 YouTube analyses per hour. Remaining: {remaining}",
        )

    video_id = extract_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    active_semaphore = separation_semaphore if separate_vocals else chord_semaphore

    with active_semaphore:
        try:
            audio_info = extract_audio(url)
            audio_path = Path(audio_info["audio_path"])

            if not audio_path.exists():
                raise HTTPException(status_code=500, detail="Failed to download audio")

            result = _run_analysis(
                audio_path,
                separate_vocals=separate_vocals,
                use_madmom=use_madmom,
            )
            _attach_instrumental_download(result, "youtube_analysis")

            audio_id = str(uuid.uuid4())
            register_files(audio_id, [str(audio_path)], type="youtube_audio")
            result["audioUrl"] = f"/api/analyze/download/{audio_id}/original.mp3"

            result["youtube"] = {
                "videoId": audio_info["video_id"],
                "title": audio_info["title"],
                "duration": audio_info["duration"],
                "thumbnail": audio_info["thumbnail"],
                "channel": audio_info.get("channel", "Unknown"),
            }
            result["remainingRequests"] = get_remaining_requests(client_ip)

            return JSONResponse(result)
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("YouTube analysis failed")
            raise HTTPException(status_code=500, detail=f"YouTube analysis failed: {exc}")


@router.get("/youtube/info")
def youtube_info(url: str):
    """Get YouTube video info without downloading."""
    try:
        info = get_video_info(url)
        return JSONResponse(info)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get video info: {exc}")


@router.get("/analyze/download/{file_id}/{filename}")
async def download_instrumental(file_id: str, filename: str):
    """Download the instrumental track produced by chord analysis."""
    entry = get_entry(file_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = Path(entry["paths"][0])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File no longer available")

    return FileResponse(file_path, media_type="audio/wav", filename=filename)
