from pathlib import Path
from urllib.parse import unquote, urlparse

from app.core.config import settings


ALLOWED_GENERATED_EXTENSIONS = {
    ".mid",
    ".midi",
    ".wav",
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

    filename = Path(
        unquote(parsed_url.path)
    ).name

    if not filename:
        return {
            "deleted": False,
            "filename": None,
            "reason": "Invalid filename",
        }

    extension = Path(
        filename
    ).suffix.lower()

    if (
        extension
        not in ALLOWED_GENERATED_EXTENSIONS
    ):
        return {
            "deleted": False,
            "filename": filename,
            "reason": (
                "Unsupported generated-file "
                "extension"
            ),
        }

    generated_directory = (
        settings.generated_dir.resolve()
    )

    target_path = (
        generated_directory / filename
    ).resolve()

    if target_path.parent != generated_directory:
        return {
            "deleted": False,
            "filename": filename,
            "reason": "Unsafe file path",
        }

    if not target_path.exists():
        return {
            "deleted": False,
            "filename": filename,
            "reason": (
                "File was already missing"
            ),
        }

    if not target_path.is_file():
        return {
            "deleted": False,
            "filename": filename,
            "reason": (
                "Generated path is not a file"
            ),
        }

    target_path.unlink()

    return {
        "deleted": True,
        "filename": filename,
        "reason": None,
    }
