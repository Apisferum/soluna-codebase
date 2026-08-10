from pathlib import Path
from urllib.parse import unquote, urlparse

from app.core.config import settings


ALLOWED_GENERATED_EXTENSIONS = {
    ".mid",
    ".midi",
    ".wav",
    ".mp3",
    ".json",
}


def delete_generated_file(
    file_url: str | None,
) -> dict[str, object]:
    if not file_url:
        return {
            "deleted": False,
            "filename": None,
            "reason": "No file path stored",
        }

    parsed_url = urlparse(str(file_url))
    filename = Path(unquote(parsed_url.path)).name

    if not filename:
        return {
            "deleted": False,
            "filename": None,
            "reason": "Invalid filename",
        }

    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_GENERATED_EXTENSIONS:
        return {
            "deleted": False,
            "filename": filename,
            "reason": "Unsupported generated-file extension",
        }

    candidates: list[Path] = []
    raw_path = Path(str(file_url)).expanduser()

    if not parsed_url.scheme and raw_path.is_absolute():
        candidates.append(raw_path)

    candidates.extend(
        [
            settings.composer_output_dir / filename,
            settings.generated_dir / filename,
        ]
    )

    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue

        if not resolved.exists():
            continue

        if not resolved.is_file():
            return {
                "deleted": False,
                "filename": filename,
                "reason": "Generated path is not a file",
            }

        resolved.unlink()
        return {
            "deleted": True,
            "filename": filename,
            "reason": None,
        }

    return {
        "deleted": False,
        "filename": filename,
        "reason": "File was already missing",
    }

