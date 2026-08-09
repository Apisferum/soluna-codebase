"""Tests for the Chord AI / Stem Separator / Voice Separator routes.

Heavy ML inference (actual Demucs/madmom runs) is intentionally not
exercised here — that needs real audio fixtures and a GPU/CPU budget this
suite shouldn't assume. These tests cover request validation, routing,
and the download/session bookkeeping, which is what regresses most easily
during a refactor like this.
"""

from fastapi.testclient import TestClient

from app.main import app


def test_analyze_requires_a_file() -> None:
    with TestClient(app) as client:
        response = client.post("/api/audio/analyze")

    assert response.status_code == 422


def test_analyze_youtube_rejects_invalid_url() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/audio/analyze-youtube",
            data={"url": "not-a-youtube-url"},
        )

    assert response.status_code == 400


def test_youtube_info_rejects_invalid_url() -> None:
    with TestClient(app) as client:
        response = client.get("/api/audio/youtube/info", params={"url": "not-a-youtube-url"})

    assert response.status_code == 400


def test_separate_requires_a_file() -> None:
    with TestClient(app) as client:
        response = client.post("/api/audio/separate")

    assert response.status_code == 422


def test_separate_rejects_bad_format() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/audio/separate",
            files={"file": ("song.wav", b"fake-audio-bytes", "audio/wav")},
            data={"format": "flac"},
        )

    assert response.status_code == 400


def test_separate_download_unknown_session_404s() -> None:
    with TestClient(app) as client:
        response = client.get("/api/audio/separate/download/does-not-exist/vocals")

    assert response.status_code == 404


def test_separate_stems_download_unknown_session_404s() -> None:
    with TestClient(app) as client:
        response = client.get("/api/audio/separate-stems/download/does-not-exist/vocals")

    assert response.status_code == 404


def test_separate_stems_download_rejects_invalid_stem_type() -> None:
    from app.services.audio_runtime import register_files

    register_files("fake-session", ["/tmp/fake.wav"], vocals="/tmp/fake.wav")

    with TestClient(app) as client:
        response = client.get("/api/audio/separate-stems/download/fake-session/kazoo")

    assert response.status_code == 400


def test_analyze_download_unknown_file_404s() -> None:
    with TestClient(app) as client:
        response = client.get("/api/audio/analyze/download/does-not-exist/instrumental.wav")

    assert response.status_code == 404
