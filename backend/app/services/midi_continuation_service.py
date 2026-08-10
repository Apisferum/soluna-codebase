from __future__ import annotations

from collections import Counter
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote, urlparse

import httpx
import mido

from app.core.config import settings


NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
MAX_UPLOAD_BYTES = 15 * 1024 * 1024


def _note_name(note: int) -> str:
    octave = (note // 12) - 1
    return f"{NOTE_NAMES[note % 12]}{octave}"


def _materialize_file(source: str, destination: Path) -> Path:
    parsed = urlparse(str(source))

    if parsed.scheme in {"http", "https"}:
        response = httpx.get(
            str(source),
            follow_redirects=True,
            timeout=max(30.0, settings.composer_http_timeout_seconds * 4),
        )
        response.raise_for_status()
        destination.write_bytes(response.content)
        return destination

    local = Path(str(source)).expanduser()
    if local.is_file():
        destination.write_bytes(local.read_bytes())
        return destination

    filename = Path(unquote(parsed.path)).name
    for directory in (settings.composer_output_dir, settings.generated_dir):
        candidate = directory / filename
        if candidate.is_file():
            destination.write_bytes(candidate.read_bytes())
            return destination

    raise FileNotFoundError(f"Composer output file could not be found: {source}")


def analyze_midi_bytes(data: bytes) -> dict[str, object]:
    if not data:
        raise ValueError("The uploaded MIDI file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValueError("The MIDI file is too large. Maximum upload size is 15 MB.")

    try:
        midi = mido.MidiFile(file=BytesIO(data))
    except Exception as error:
        raise ValueError("The uploaded file is not a readable MIDI file.") from error

    note_counts: Counter[int] = Counter()
    channel_counts: Counter[int] = Counter()
    programs: dict[int, int] = {}
    tempos: list[int] = []
    timed_notes: list[tuple[int, int]] = []
    duration_ticks = 0

    for track in midi.tracks:
        track_ticks = 0
        for message in track:
            track_ticks += int(message.time)
            if message.type == "set_tempo":
                tempos.append(int(message.tempo))
            elif message.type == "program_change":
                programs[int(message.channel)] = int(message.program)
            elif message.type == "note_on" and int(message.velocity) > 0:
                note = int(message.note)
                note_counts[note] += 1
                channel_counts[int(message.channel)] += 1
                timed_notes.append((track_ticks, note))
        duration_ticks = max(duration_ticks, track_ticks)

    if not note_counts:
        raise ValueError("The MIDI file contains no note-on events to continue from.")

    tempo = tempos[0] if tempos else mido.bpm2tempo(120)
    bpm = int(round(mido.tempo2bpm(tempo)))
    duration_beats = duration_ticks / max(1, midi.ticks_per_beat)
    duration_seconds = mido.tick2second(duration_ticks, midi.ticks_per_beat, tempo)

    note_sequence = [note for _, note in sorted(timed_notes, key=lambda item: item[0])]
    common_notes = [
        _note_name(note)
        for note, _ in note_counts.most_common(8)
    ]
    ending_notes = [_note_name(note) for note in note_sequence[-16:]]
    pitch_classes = Counter(note % 12 for note in note_sequence)
    common_pitch_classes = [
        NOTE_NAMES[pitch_class]
        for pitch_class, _ in pitch_classes.most_common(5)
    ]

    return {
        "midi_type": midi.type,
        "tracks": len(midi.tracks),
        "ticks_per_beat": midi.ticks_per_beat,
        "tempo_bpm": bpm,
        "duration_beats": round(duration_beats, 2),
        "duration_seconds": round(duration_seconds, 2),
        "note_events": sum(note_counts.values()),
        "lowest_note": _note_name(min(note_counts)),
        "highest_note": _note_name(max(note_counts)),
        "common_notes": common_notes,
        "common_pitch_classes": common_pitch_classes,
        "ending_notes": ending_notes,
        "programs": programs,
        "channels": sorted(channel_counts),
    }


def build_continuation_prompt(
    source_summary: dict[str, object],
    genre: str,
    complexity: int,
    tempo_match: bool,
    tempo_bpm: int,
) -> str:
    source_bpm = int(source_summary["tempo_bpm"])
    target_bpm = source_bpm if tempo_match else max(30, min(300, int(tempo_bpm)))
    common_notes = ", ".join(source_summary.get("common_notes", []))
    ending_notes = ", ".join(source_summary.get("ending_notes", []))
    pitch_classes = ", ".join(source_summary.get("common_pitch_classes", []))

    return (
        "Continue an existing MIDI composition rather than starting a disconnected new song. "
        f"Target style: {genre}. Target tempo: {target_bpm} BPM. Arrangement complexity: {complexity}/100. "
        f"The source fragment has {source_summary['tracks']} track(s), approximately "
        f"{source_summary['duration_beats']} beats, pitch range {source_summary['lowest_note']} to "
        f"{source_summary['highest_note']}, and dominant pitch classes {pitch_classes}. "
        f"Frequently used notes are {common_notes}. The final note sequence is {ending_notes}. "
        "Preserve the established rhythmic density, tonal center, phrase shape, and register. "
        "Begin the generated material as a natural next phrase, develop the existing motif, avoid a fresh intro, "
        "and create a coherent continuation with a satisfying build and ending."
    )


def _copy_track(track: mido.MidiTrack, scale: float = 1.0, initial_delay: int = 0) -> mido.MidiTrack:
    copied = mido.MidiTrack()
    delayed = False

    for message in track:
        if message.type == "end_of_track":
            continue
        delta = max(0, int(round(float(message.time) * scale)))
        if not delayed:
            delta += initial_delay
            delayed = True
        copied.append(message.copy(time=delta))

    copied.append(mido.MetaMessage("end_of_track", time=0))
    return copied


def append_midi(source_bytes: bytes, continuation_path: Path, output_path: Path) -> None:
    source = mido.MidiFile(file=BytesIO(source_bytes))
    continuation = mido.MidiFile(str(continuation_path))

    output = mido.MidiFile(type=1, ticks_per_beat=source.ticks_per_beat)

    source_end_ticks = 0
    for track in source.tracks:
        source_end_ticks = max(source_end_ticks, sum(int(message.time) for message in track))
        output.tracks.append(_copy_track(track))

    continuation_scale = source.ticks_per_beat / max(1, continuation.ticks_per_beat)
    one_beat_gap = source.ticks_per_beat
    delay = source_end_ticks + one_beat_gap

    for track in continuation.tracks:
        output.tracks.append(
            _copy_track(
                track,
                scale=continuation_scale,
                initial_delay=delay,
            )
        )

    output.save(str(output_path))


def continue_midi(
    task_id: str,
    source_bytes: bytes,
    source_filename: str,
    genre: str,
    complexity: int,
    tempo_match: bool,
    tempo_bpm: int,
    use_mock_llm: bool = False,
) -> dict[str, object]:
    source_summary = analyze_midi_bytes(source_bytes)
    continuation_prompt = build_continuation_prompt(
        source_summary=source_summary,
        genre=genre,
        complexity=max(0, min(100, int(complexity))),
        tempo_match=tempo_match,
        tempo_bpm=tempo_bpm,
    )

    # Import lazily so MIDI validation/analysis can run without loading the
    # Celery/composer stack until generation is actually requested.
    from app.services.composer_service import run_composer_generation

    result = run_composer_generation(
        task_id=task_id,
        prompt=continuation_prompt,
        use_mock_llm=use_mock_llm,
    )

    midi_source = result.get("midi_path")
    if not midi_source:
        raise RuntimeError("Composer completed without producing continuation MIDI.")

    settings.composer_output_dir.mkdir(parents=True, exist_ok=True)
    generated_piece_path = settings.composer_output_dir / f"{task_id}_generated_part.mid"
    combined_path = settings.composer_output_dir / f"{task_id}_continued.mid"
    blueprint_path = settings.composer_output_dir / f"{task_id}_continuation_blueprint.json"

    _materialize_file(str(midi_source), generated_piece_path)
    append_midi(source_bytes, generated_piece_path, combined_path)

    blueprint_source = result.get("blueprint_path")
    materialized_blueprint_path: Path | None = None
    if blueprint_source:
        materialized_blueprint_path = _materialize_file(
            str(blueprint_source),
            blueprint_path,
        )

    return {
        "status": "completed",
        "source_filename": Path(source_filename).name,
        "source_summary": source_summary,
        "continuation_prompt": continuation_prompt,
        "midi_path": str(combined_path),
        "blueprint_path": (
            str(materialized_blueprint_path)
            if materialized_blueprint_path is not None
            else None
        ),
        "message": "MIDI continuation generated and appended to the uploaded source.",
    }
