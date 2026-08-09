from typing import Literal

from pydantic import BaseModel

AudioFormat = Literal["wav", "mp3"]


class SeparateResponse(BaseModel):
    session_id: str
    format: AudioFormat
    vocalsUrl: str
    instrumentalUrl: str


class StemSeparateResponse(BaseModel):
    session_id: str
    format: AudioFormat
    stems: list[str]
    vocalsUrl: str | None = None
    drumsUrl: str | None = None
    bassUrl: str | None = None
    guitarUrl: str | None = None
    pianoUrl: str | None = None
    otherUrl: str | None = None


# Note: /analyze, /analyze-youtube and /youtube/info intentionally return
# plain dicts rather than a strict response_model. Their exact key set
# depends on which analysis engine ran (madmom vs librosa) and whether
# vocal separation was requested, so a fixed schema would risk silently
# dropping fields the frontend relies on.
