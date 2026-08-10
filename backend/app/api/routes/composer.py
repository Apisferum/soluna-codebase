import os
import uuid
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from celery.result import AsyncResult

from app.core.config import settings
from app.tasks.composer import celery_app, generate_song_task
from app.services.midi_continuation_service import continue_midi

router = APIRouter()

ALLOWED_DOWNLOAD_EXTENSIONS = {".mid", ".json"}


class GenerateRequest(BaseModel):
    prompt: str
    use_mock_llm: bool = False


@router.post("/generate")
def generate_music(req: GenerateRequest):
    task_id = str(uuid.uuid4())
    task = generate_song_task.delay(task_id, req.prompt, req.use_mock_llm)

    return {
        "task_id": task_id,
        "celery_task_id": task.id,
        "status": "queued",
        "message": "Composer generation task pushed to queue."
    }


@router.get("/status/{celery_task_id}")
def get_status(celery_task_id: str):
    task_result = AsyncResult(celery_task_id, app=celery_app)

    if task_result.state == 'PENDING':
        return {"status": "queued", "progress": "Waiting for available GPU worker..."}
    elif task_result.state in ['LOADING_MODELS', 'PLANNING', 'COMPOSING']:
        info = task_result.info or {}
        return {
            "status": "processing",
            "stage": task_result.state,
            "progress": info.get('progress', 'Working...')
        }
    elif task_result.state == 'SUCCESS':
        info = task_result.info or {}
        midi_path = info.get('midi_path')
        blueprint_path = info.get('blueprint_path')
        if not midi_path or not blueprint_path:
            return {"status": "failed", "error": "Task reported success but produced no output paths."}
        return {
            "status": "completed",
            "midi_download_url": f"/api/composer/download/{os.path.basename(midi_path)}",
            "blueprint_download_url": f"/api/composer/download/{os.path.basename(blueprint_path)}"
        }
    elif task_result.state == 'FAILURE':
        info = task_result.info
        error_msg = info.get('error') if isinstance(info, dict) else str(info)
        return {"status": "failed", "error": error_msg}
    else:
        return {"status": task_result.state}


@router.post("/continue-midi")
async def continue_uploaded_midi(
    file: UploadFile = File(...),
    genre: str = Form("classical"),
    complexity: int = Form(75),
    tempo_match: bool = Form(True),
    tempo_bpm: int = Form(120),
    use_mock_llm: bool = Form(False),
):
    filename = file.filename or "source.mid"
    extension = os.path.splitext(filename)[1].lower()
    if extension not in {".mid", ".midi"}:
        raise HTTPException(status_code=400, detail="Please upload a MIDI (.mid or .midi) file.")

    source_bytes = await file.read()
    task_id = str(uuid.uuid4())

    try:
        result = await run_in_threadpool(
            continue_midi,
            task_id=task_id,
            source_bytes=source_bytes,
            source_filename=filename,
            genre=genre.strip() or "classical",
            complexity=complexity,
            tempo_match=tempo_match,
            tempo_bpm=tempo_bpm,
            use_mock_llm=use_mock_llm,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"MIDI continuation failed: {error}") from error

    midi_path = str(result["midi_path"])
    blueprint_path = result.get("blueprint_path")

    return {
        "status": "completed",
        "message": result["message"],
        "source_filename": result["source_filename"],
        "source_summary": result["source_summary"],
        "midi_download_url": f"/api/composer/download/{os.path.basename(midi_path)}",
        "blueprint_download_url": (
            f"/api/composer/download/{os.path.basename(str(blueprint_path))}"
            if blueprint_path
            else None
        ),
    }


@router.get("/download/{file_name}")
def download_file(file_name: str):
    _, ext = os.path.splitext(file_name)
    if ext.lower() not in ALLOWED_DOWNLOAD_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    output_dir = str(settings.composer_output_dir)
    candidate = os.path.normpath(os.path.join(output_dir, file_name))
    if os.path.dirname(candidate) != os.path.normpath(output_dir):
        raise HTTPException(status_code=400, detail="Invalid filename.")

    if not os.path.isfile(candidate):
        raise HTTPException(status_code=404, detail="File not found")

    media_type = "audio/midi" if candidate.endswith(".mid") else "application/json"
    return FileResponse(candidate, media_type=media_type, filename=file_name)
