"""Verifies the madmom engine module loads safely when madmom itself is
optional / not installed, and falls back the way callers expect.

Ported from the old services/audio_api/tests manual script into a real
pytest test.
"""

from pathlib import Path

from app.music.chord_madmom import MADMOM_AVAILABLE, analyze_file_madmom


def test_madmom_module_loads_without_crashing() -> None:
    # Just importing the module (done above) should never raise, whether
    # or not the optional madmom dependency is installed.
    assert isinstance(MADMOM_AVAILABLE, bool)


def test_analyze_file_madmom_handles_missing_file_gracefully() -> None:
    missing_file = Path("nonexistent.wav")

    try:
        analyze_file_madmom(missing_file)
    except ImportError:
        # Expected when madmom isn't installed in this environment.
        assert not MADMOM_AVAILABLE
    except (OSError, RuntimeError):
        # Expected: librosa/soundfile raising because the file doesn't
        # exist when madmom is installed. We assert madmom is available
        # to ensure it wasn't a silent crash from an optional import issue.
        assert MADMOM_AVAILABLE
