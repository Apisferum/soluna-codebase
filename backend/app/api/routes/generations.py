from contextlib import closing
import json
from pathlib import Path
from urllib.parse import unquote, urlparse
import time
import httpx

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import (
    get_current_user,
    normalize_email,
    require_admin,
)
from app.db.database import connect_db
from app.schemas.generation import (
    AdminGenerationsResponse,
    DeleteGenerationResponse,
    UserGenerationsResponse,
)
from app.services.generated_file_service import (
    delete_generated_file,
)
from app.services.composer_service import run_composer_generation


router = APIRouter()


ALLOWED_GENERATION_EXTENSIONS = {".mid", ".midi", ".wav", ".mp3", ".json"}


def generation_asset_url(
    generation_id: int,
    asset_type: str,
    stored_path: str | None,
) -> str | None:
    if not stored_path:
        return None

    return f"/generations/{generation_id}/download/{asset_type}"


def parse_json_value(value: str | None, fallback):
    if not value:
        return fallback

    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return fallback


def resolve_stored_asset(stored_path: str) -> tuple[Path | None, str | None]:
    parsed = urlparse(str(stored_path))
    filename = Path(unquote(parsed.path)).name

    if not filename:
        return None, None

    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_GENERATION_EXTENSIONS:
        return None, None

    candidates: list[Path] = []

    raw_path = Path(str(stored_path)).expanduser()
    if not parsed.scheme and raw_path.is_absolute():
        candidates.append(raw_path)

    for directory in (
        settings.composer_output_dir,
        settings.generated_dir,
    ):
        candidates.append(directory / filename)

    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue

        if resolved.is_file():
            return resolved, None

    if parsed.scheme in {"http", "https"}:
        return None, str(stored_path)

    return None, None


class GenerateRequest(BaseModel):
    prompt: str
    mood: str
    genre: str
    tempo: str
    instrument: str
    structure: str


def json_dumps_or_none(value) -> str | None:
    if value is None:
        return None
    try:
        return json.dumps(value)
    except Exception:
        return None


@router.post(
    "/generate",
    status_code=status.HTTP_201_CREATED,
)
def create_generation_unified(
    data: GenerateRequest,
    response: Response,
    current_user=Depends(get_current_user),
):
    """Proxy endpoint for generation requests in the unified backend.

    Generates music assets through the integrated composer, saves metadata to the DB,
    and returns a structured response matching frontend expectations.
    """
    if not data.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt is required",
        )

    user_email = normalize_email(current_user["email"])

    try:
        generation_result = run_composer_generation(
            task_id=str(int(time.time() * 1000)),
            prompt=data.prompt,
            use_mock_llm=False,
        )

        music_spec = {}
        structured_plan = {}
        routing = {}
        critic_trace = []
        coherence_scores = []
        generated_midi_path = generation_result.get("midi_path")
        generated_blueprint_path = generation_result.get("blueprint_path")
        generated_audio_path = None
        generation_status = "completed"
        message = generation_result.get("message", "AI Plan generated successfully.")

    except Exception as error:
        generation_status = "failed"
        message = f"Composer generation failed: {str(error)}"
        music_spec = {}
        structured_plan = {}
        routing = {}
        critic_trace = []
        coherence_scores = []
        generated_midi_path = None
        generated_blueprint_path = None
        generated_audio_path = None

    planner_mood = music_spec.get("mood")
    planner_genre = music_spec.get("genre")
    planner_tempo = music_spec.get("tempo")
    planner_instrumentation = music_spec.get("instrumentation")

    resolved_mood = str(planner_mood or data.mood).strip()
    resolved_genre = str(planner_genre or data.genre).strip()
    resolved_tempo = str(planner_tempo or data.tempo).strip()

    planner_key = music_spec.get("key")
    resolved_key = str(planner_key).strip() if planner_key else None

    if isinstance(planner_instrumentation, list):
        resolved_instrument = ", ".join(
            str(instrument).strip()
            for instrument in planner_instrumentation
            if str(instrument).strip()
        )
    elif planner_instrumentation:
        resolved_instrument = str(planner_instrumentation).strip()
    else:
        resolved_instrument = data.instrument

    planned_sections = []
    if isinstance(structured_plan, dict):
        possible_sections = structured_plan.get("sections")
        if isinstance(possible_sections, list):
            planned_sections = possible_sections

    section_names = []
    for section in planned_sections:
        if not isinstance(section, dict):
            continue
        section_name = str(section.get("name") or "").strip()
        if section_name:
            section_names.append(section_name)

    resolved_structure = (
        " → ".join(section_names)
        if section_names
        else data.structure
    )

    with closing(connect_db()) as connection:
        cursor = connection.cursor()
        now = int(time.time())

        cursor.execute(
            """
            INSERT INTO generations (
                user_email,
                prompt,
                mood,
                genre,
                tempo,
                music_key,
                instrument,
                structure,
                status,
                message,
                midi_notes,
                midi_file_path,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_email,
                data.prompt,
                resolved_mood,
                resolved_genre,
                resolved_tempo,
                resolved_key,
                resolved_instrument,
                resolved_structure,
                generation_status,
                message,
                json.dumps(structured_plan),
                generated_midi_path,
                now,
            ),
        )

        generation_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO generation_analysis (
                generation_id,
                original_prompt,
                intent_json,
                structure_plan_json,
                routing_json,
                critic_trace_json,
                midi_file_path,
                audio_file_path,
                blueprint_file_path,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(generation_id) DO UPDATE SET
                original_prompt = excluded.original_prompt,
                intent_json = excluded.intent_json,
                structure_plan_json = excluded.structure_plan_json,
                routing_json = excluded.routing_json,
                critic_trace_json = excluded.critic_trace_json,
                midi_file_path = excluded.midi_file_path,
                audio_file_path = excluded.audio_file_path,
                blueprint_file_path = excluded.blueprint_file_path,
                updated_at = excluded.updated_at
            """,
            (
                generation_id,
                data.prompt,
                json_dumps_or_none(music_spec),
                json_dumps_or_none(structured_plan),
                json_dumps_or_none(routing),
                json_dumps_or_none(critic_trace),
                generated_midi_path,
                generated_audio_path,
                generated_blueprint_path,
                now,
                now,
            ),
        )

        if isinstance(coherence_scores, dict):
            coherence_scores = [
                {"sectionName": "global", **coherence_scores}
            ]

        if isinstance(coherence_scores, list):
            for score in coherence_scores:
                if not isinstance(score, dict):
                    continue

                section_name = str(
                    score.get("sectionName")
                    or score.get("section_name")
                    or "global"
                ).strip() or "global"

                cursor.execute(
                    """
                    INSERT INTO coherence_scores (
                        generation_id,
                        section_name,
                        chord_adherence,
                        harmonic_stability,
                        rhythmic_regularity,
                        motif_similarity,
                        density_fidelity,
                        transition_quality,
                        emotional_alignment,
                        prompt_alignment,
                        overall_score,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(generation_id, section_name) DO UPDATE SET
                        chord_adherence = excluded.chord_adherence,
                        harmonic_stability = excluded.harmonic_stability,
                        rhythmic_regularity = excluded.rhythmic_regularity,
                        motif_similarity = excluded.motif_similarity,
                        density_fidelity = excluded.density_fidelity,
                        transition_quality = excluded.transition_quality,
                        emotional_alignment = excluded.emotional_alignment,
                        prompt_alignment = excluded.prompt_alignment,
                        overall_score = excluded.overall_score,
                        created_at = excluded.created_at
                    """,
                    (
                        generation_id,
                        section_name,
                        score.get("chordAdherence", score.get("chord_adherence")),
                        score.get("harmonicStability", score.get("harmonic_stability")),
                        score.get("rhythmicRegularity", score.get("rhythmic_regularity")),
                        score.get("motifSimilarity", score.get("motif_similarity")),
                        score.get("densityFidelity", score.get("density_fidelity")),
                        score.get("transitionQuality", score.get("transition_quality")),
                        score.get("emotionalAlignment", score.get("emotional_alignment")),
                        score.get("promptAlignment", score.get("prompt_alignment")),
                        score.get("overallScore", score.get("overall_score")),
                        now,
                    ),
                )

        connection.commit()

    if generation_status == "completed":
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_502_BAD_GATEWAY

    return {
        "message": message,
        "request": {
            "id": generation_id,
            "title": (
                data.prompt[:42] + "..."
                if len(data.prompt) > 42
                else data.prompt
            ),
            "prompt": data.prompt,
            "fullPrompt": data.prompt,
            "mood": resolved_mood,
            "genre": resolved_genre,
            "tempo": resolved_tempo,
            "key": resolved_key,
            "instrument": resolved_instrument,
            "structure": resolved_structure,
            "status": generation_status,
            "message": message,
            "musicSpec": music_spec,
            "structuredPlan": structured_plan,
            "routing": routing,
            "criticTrace": critic_trace,
            "coherenceScores": coherence_scores,
            "midiFilePath": generation_asset_url(
                generation_id, "midi", generated_midi_path
            ),
            "blueprintFilePath": generation_asset_url(
                generation_id, "blueprint", generated_blueprint_path
            ),
            "audioFilePath": generation_asset_url(
                generation_id, "audio", generated_audio_path
            ),
        },
    }


def parse_structured_plan(
    value: str | None,
) -> dict:
    if not value:
        return {}

    try:
        result = json.loads(value)
    except (
        TypeError,
        json.JSONDecodeError,
    ):
        return {}

    return (
        result
        if isinstance(result, dict)
        else {}
    )


def create_generation_title(
    prompt: str,
) -> str:
    if len(prompt) > 42:
        return prompt[:42] + "."

    return prompt


@router.get(
    "/generations",
    response_model=UserGenerationsResponse,
)
def get_generations(
    current_user=Depends(
        get_current_user
    ),
) -> UserGenerationsResponse:
    user_email = normalize_email(
        current_user["email"]
    )

    with closing(connect_db()) as connection:
        rows = connection.execute(
            """
            SELECT
                g.id,
                g.prompt,
                g.mood,
                g.genre,
                g.tempo,
                g.music_key,
                g.instrument,
                g.structure,
                g.status,
                g.message,
                g.midi_notes,
                COALESCE(
                    ga.midi_file_path,
                    g.midi_file_path
                ) AS resolved_midi_file_path,
                ga.audio_file_path
                    AS audio_file_path,
                ga.blueprint_file_path
                    AS blueprint_file_path,
                g.created_at
            FROM generations AS g
            LEFT JOIN generation_analysis AS ga
                ON ga.generation_id = g.id
            WHERE LOWER(g.user_email) = ?
            ORDER BY g.created_at DESC
            """,
            (user_email,),
        ).fetchall()

    generations = []

    for row in rows:
        prompt = row["prompt"]

        structured_plan = (
            parse_structured_plan(
                row["midi_notes"]
            )
        )

        generations.append(
            {
                "id": row["id"],
                "title": (
                    create_generation_title(
                        prompt
                    )
                ),
                "prompt": prompt,
                "fullPrompt": prompt,
                "mood": row["mood"],
                "genre": row["genre"],
                "tempo": row["tempo"],
                "key": row["music_key"],
                "instrument": (
                    row["instrument"]
                ),
                "structure": row["structure"],
                "status": (
                    row["status"]
                    or "pending"
                ),
                "message": row["message"],
                "structuredPlan": (
                    structured_plan
                ),
                "midiNotes": (
                    structured_plan
                ),
                "midiFilePath": generation_asset_url(
                    row["id"],
                    "midi",
                    row["resolved_midi_file_path"],
                ),
                "blueprintFilePath": generation_asset_url(
                    row["id"],
                    "blueprint",
                    row["blueprint_file_path"],
                ),
                "audioFilePath": generation_asset_url(
                    row["id"],
                    "audio",
                    row["audio_file_path"],
                ),
                "createdAt": row[
                    "created_at"
                ],
            }
        )

    return UserGenerationsResponse(
        generations=generations
    )


@router.delete(
    "/generations/{generation_id}",
    response_model=DeleteGenerationResponse,
)
def delete_user_generation(
    generation_id: int,
    current_user=Depends(
        get_current_user
    ),
) -> DeleteGenerationResponse:
    user_email = normalize_email(
        current_user["email"]
    )

    with closing(connect_db()) as connection:
        generation = connection.execute(
            """
            SELECT
                g.id,
                COALESCE(
                    ga.midi_file_path,
                    g.midi_file_path
                ) AS midi_file_path,
                ga.audio_file_path
                    AS audio_file_path,
                ga.blueprint_file_path
                    AS blueprint_file_path
            FROM generations AS g
            LEFT JOIN generation_analysis AS ga
                ON ga.generation_id = g.id
            WHERE g.id = ?
              AND LOWER(g.user_email) = ?
            """,
            (
                generation_id,
                user_email,
            ),
        ).fetchone()

        if generation is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail="Generation not found",
            )

        midi_file_path = generation[
            "midi_file_path"
        ]

        audio_file_path = generation[
            "audio_file_path"
        ]

        blueprint_file_path = generation[
            "blueprint_file_path"
        ]

        connection.execute(
            """
            DELETE FROM generations
            WHERE id = ?
              AND LOWER(user_email) = ?
            """,
            (
                generation_id,
                user_email,
            ),
        )

        connection.commit()

    cleanup_results = []

    unique_file_paths = dict.fromkeys(
        [
            midi_file_path,
            audio_file_path,
            blueprint_file_path,
        ]
    )

    for file_path in unique_file_paths:
        if not file_path:
            continue

        try:
            cleanup_results.append(
                delete_generated_file(
                    file_path
                )
            )
        except OSError as error:
            cleanup_results.append(
                {
                    "deleted": False,
                    "filename": Path(
                        urlparse(
                            str(file_path)
                        ).path
                    ).name,
                    "reason": str(error),
                }
            )

    return DeleteGenerationResponse(
        message=(
            "Generation deleted successfully"
        ),
        generationId=generation_id,
        fileCleanup=cleanup_results,
    )


@router.get(
    "/admin/generations",
    response_model=AdminGenerationsResponse,
)
def get_admin_generations(
    current_admin=Depends(
        require_admin
    ),
) -> AdminGenerationsResponse:
    del current_admin

    with closing(connect_db()) as connection:
        rows = connection.execute(
            """
            SELECT
                g.*,
                COALESCE(ga.midi_file_path, g.midi_file_path)
                    AS resolved_midi_file_path,
                ga.audio_file_path AS resolved_audio_file_path,
                ga.blueprint_file_path AS resolved_blueprint_file_path
            FROM generations AS g
            LEFT JOIN generation_analysis AS ga
                ON ga.generation_id = g.id
            ORDER BY g.created_at DESC
            """
        ).fetchall()

    generations = []

    for row in rows:
        prompt = row["prompt"]

        structured_plan = (
            parse_structured_plan(
                row["midi_notes"]
            )
        )

        generations.append(
            {
                "id": row["id"],
                "userEmail": (
                    row["user_email"]
                ),
                "title": (
                    create_generation_title(
                        prompt
                    )
                ),
                "prompt": prompt,
                "fullPrompt": prompt,
                "mood": row["mood"],
                "genre": row["genre"],
                "tempo": row["tempo"],
                "key": row["music_key"],
                "instrument": (
                    row["instrument"]
                ),
                "structure": row["structure"],
                "status": (
                    row["status"]
                    or "pending"
                ),
                "message": row["message"],
                "structuredPlan": (
                    structured_plan
                ),
                "midiNotes": (
                    structured_plan
                ),
                "midiFilePath": generation_asset_url(
                    row["id"],
                    "midi",
                    row["resolved_midi_file_path"],
                ),
                "blueprintFilePath": generation_asset_url(
                    row["id"],
                    "blueprint",
                    row["resolved_blueprint_file_path"],
                ),
                "createdAt": row[
                    "created_at"
                ],
            }
        )

    return AdminGenerationsResponse(
        generations=generations
    )

@router.get("/generations/{generation_id}/download/{asset_type}")
def download_generation_asset(
    generation_id: int,
    asset_type: str,
    current_user=Depends(get_current_user),
):
    if asset_type not in {"midi", "audio", "blueprint"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported generation asset type",
        )

    with closing(connect_db()) as connection:
        row = connection.execute(
            """
            SELECT
                g.user_email,
                COALESCE(ga.midi_file_path, g.midi_file_path)
                    AS midi_file_path,
                ga.audio_file_path AS audio_file_path,
                ga.blueprint_file_path AS blueprint_file_path
            FROM generations AS g
            LEFT JOIN generation_analysis AS ga
                ON ga.generation_id = g.id
            WHERE g.id = ?
            """,
            (generation_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found",
        )

    requester_email = normalize_email(current_user["email"])
    owner_email = normalize_email(row["user_email"])
    requester_role = str(current_user["role"] or "user").strip().lower()

    if requester_email != owner_email and requester_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this generation",
        )

    stored_path = {
        "midi": row["midi_file_path"],
        "audio": row["audio_file_path"],
        "blueprint": row["blueprint_file_path"],
    }[asset_type]

    if not stored_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generated {asset_type} file is unavailable",
        )

    local_path, remote_url = resolve_stored_asset(str(stored_path))

    if local_path is not None:
        suffix = local_path.suffix.lower()
        media_type = {
            ".mid": "audio/midi",
            ".midi": "audio/midi",
            ".wav": "audio/wav",
            ".mp3": "audio/mpeg",
            ".json": "application/json",
        }.get(suffix, "application/octet-stream")

        return FileResponse(
            str(local_path),
            media_type=media_type,
            filename=local_path.name,
        )

    if remote_url:
        try:
            remote_response = httpx.get(
                remote_url,
                follow_redirects=True,
                timeout=max(30.0, settings.composer_http_timeout_seconds * 4),
            )
            remote_response.raise_for_status()
        except httpx.HTTPError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not retrieve the generated file from the remote composer",
            ) from error

        filename = Path(unquote(urlparse(remote_url).path)).name or (
            f"generation-{generation_id}.{
                'mid' if asset_type == 'midi' else 'json' if asset_type == 'blueprint' else 'wav'
            }"
        )
        suffix = Path(filename).suffix.lower()
        media_type = {
            ".mid": "audio/midi",
            ".midi": "audio/midi",
            ".wav": "audio/wav",
            ".mp3": "audio/mpeg",
            ".json": "application/json",
        }.get(suffix, remote_response.headers.get("content-type", "application/octet-stream"))

        return Response(
            content=remote_response.content,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Generated file no longer exists on the server",
    )


@router.get("/admin/generations/{generation_id}/analysis")
def get_admin_generation_analysis(
    generation_id: int,
    current_admin=Depends(require_admin),
):
    del current_admin

    with closing(connect_db()) as connection:
        analysis = connection.execute(
            """
            SELECT
                ga.generation_id,
                ga.original_prompt,
                ga.intent_json,
                ga.structure_plan_json,
                ga.routing_json,
                ga.critic_trace_json,
                COALESCE(ga.midi_file_path, g.midi_file_path)
                    AS midi_file_path,
                ga.audio_file_path,
                ga.blueprint_file_path
            FROM generation_analysis AS ga
            JOIN generations AS g
                ON g.id = ga.generation_id
            WHERE ga.generation_id = ?
            """,
            (generation_id,),
        ).fetchone()

        if analysis is None:
            generation = connection.execute(
                """
                SELECT id, prompt, midi_file_path
                FROM generations
                WHERE id = ?
                """,
                (generation_id,),
            ).fetchone()

            if generation is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Generation not found",
                )

            return {
                "generationId": generation["id"],
                "originalPrompt": generation["prompt"],
                "intent": {},
                "structurePlan": {},
                "routing": {},
                "criticTrace": [],
                "midiFilePath": generation_asset_url(
                    generation["id"], "midi", generation["midi_file_path"]
                ),
                "audioFilePath": None,
                "blueprintFilePath": None,
                "coherenceScores": [],
            }

        score_rows = connection.execute(
            """
            SELECT *
            FROM coherence_scores
            WHERE generation_id = ?
            ORDER BY id ASC
            """,
            (generation_id,),
        ).fetchall()

    coherence_scores = [
        {
            "sectionName": row["section_name"],
            "chordAdherence": row["chord_adherence"],
            "harmonicStability": row["harmonic_stability"],
            "rhythmicRegularity": row["rhythmic_regularity"],
            "motifSimilarity": row["motif_similarity"],
            "densityFidelity": row["density_fidelity"],
            "transitionQuality": row["transition_quality"],
            "emotionalAlignment": row["emotional_alignment"],
            "promptAlignment": row["prompt_alignment"],
            "overallScore": row["overall_score"],
        }
        for row in score_rows
    ]

    return {
        "generationId": analysis["generation_id"],
        "originalPrompt": analysis["original_prompt"],
        "intent": parse_json_value(analysis["intent_json"], {}),
        "structurePlan": parse_json_value(
            analysis["structure_plan_json"], {}
        ),
        "routing": parse_json_value(analysis["routing_json"], {}),
        "criticTrace": parse_json_value(analysis["critic_trace_json"], []),
        "midiFilePath": generation_asset_url(
            analysis["generation_id"], "midi", analysis["midi_file_path"]
        ),
        "audioFilePath": generation_asset_url(
            analysis["generation_id"], "audio", analysis["audio_file_path"]
        ),
        "blueprintFilePath": generation_asset_url(
            analysis["generation_id"], "blueprint", analysis["blueprint_file_path"]
        ),
        "coherenceScores": coherence_scores,
    }

