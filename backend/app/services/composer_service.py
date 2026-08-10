from __future__ import annotations

import time
from urllib.parse import urljoin

import httpx
from celery.exceptions import TimeoutError as CeleryTimeoutError

from app.core.config import settings
from app.tasks.composer import generate_song_task, run_generation


def _remote_composer_api_base() -> str | None:
    configured = settings.composer_remote_api_url
    if not configured:
        return None

    base = configured.strip().rstrip("/")
    if not base:
        return None

    if base.endswith("/api/composer"):
        return base
    if base.endswith("/api"):
        return f"{base}/composer"
    return f"{base}/api/composer"


def _absolute_remote_url(api_base: str, path: str | None) -> str | None:
    if not path:
        return None

    if path.startswith(("http://", "https://")):
        return path

    return urljoin(f"{api_base}/", path)


def _run_remote_generation(
    api_base: str,
    prompt: str,
    use_mock_llm: bool,
) -> dict:
    request_timeout = max(5.0, settings.composer_http_timeout_seconds)
    poll_interval = max(0.5, settings.composer_poll_interval_seconds)
    deadline = time.monotonic() + settings.celery_task_time_limit

    with httpx.Client(
        timeout=request_timeout,
        follow_redirects=True,
    ) as client:
        queued_response = client.post(
            f"{api_base}/generate",
            json={
                "prompt": prompt,
                "use_mock_llm": use_mock_llm,
            },
        )
        queued_response.raise_for_status()
        queued = queued_response.json()

        celery_task_id = queued.get("celery_task_id")
        if not celery_task_id:
            raise RuntimeError(
                "Remote composer did not return a Celery task id."
            )

        while time.monotonic() < deadline:
            status_response = client.get(
                f"{api_base}/status/{celery_task_id}"
            )
            status_response.raise_for_status()
            result = status_response.json()
            state = str(result.get("status", "")).strip().lower()

            if state == "completed":
                midi_url = _absolute_remote_url(
                    api_base,
                    result.get("midi_download_url"),
                )
                blueprint_url = _absolute_remote_url(
                    api_base,
                    result.get("blueprint_download_url"),
                )

                if not midi_url:
                    raise RuntimeError(
                        "Remote composer completed without a MIDI download URL."
                    )

                return {
                    "status": "completed",
                    "midi_path": midi_url,
                    "blueprint_path": blueprint_url,
                    "message": "Masterpiece rendered.",
                }

            if state == "failed":
                raise RuntimeError(
                    str(result.get("error") or "Remote composer generation failed.")
                )

            time.sleep(poll_interval)

    raise TimeoutError(
        "Remote composer did not finish before the configured generation timeout."
    )


def _run_celery_generation(
    task_id: str,
    prompt: str,
    use_mock_llm: bool,
) -> dict:
    task = generate_song_task.delay(
        task_id,
        prompt,
        use_mock_llm,
    )

    try:
        result = task.get(
            timeout=settings.celery_task_time_limit,
            propagate=True,
        )
    except CeleryTimeoutError as error:
        task.revoke(terminate=False)
        raise TimeoutError(
            "Composer worker did not finish before the configured generation timeout."
        ) from error

    if not isinstance(result, dict):
        raise RuntimeError(
            "Composer worker returned an invalid generation result."
        )

    return result


def run_composer_generation(
    task_id: str,
    prompt: str,
    use_mock_llm: bool = False,
) -> dict:
    """Run generation outside the FastAPI process whenever possible.

    Priority:
      1. COMPOSER_REMOTE_API_URL -> remote composer service (e.g. Kaggle tunnel)
      2. COMPOSER_EXECUTION_MODE=celery -> local/shared Celery worker
      3. COMPOSER_EXECUTION_MODE=direct -> explicit development fallback
    """
    remote_api_base = _remote_composer_api_base()
    if remote_api_base:
        return _run_remote_generation(
            remote_api_base,
            prompt,
            use_mock_llm,
        )

    mode = settings.composer_execution_mode.strip().lower()

    if mode == "celery":
        return _run_celery_generation(
            task_id,
            prompt,
            use_mock_llm,
        )

    if mode == "direct":
        return run_generation(
            task_id=task_id,
            prompt=prompt,
            use_mock_llm=use_mock_llm,
        )

    raise RuntimeError(
        "COMPOSER_EXECUTION_MODE must be either 'celery' or 'direct'."
    )
