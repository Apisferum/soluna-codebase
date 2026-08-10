# Synestra Unified Backend

The backend now runs as one FastAPI application on port **8000**. Authentication, users, admin, generation history, composer endpoints, chord analysis, stem separation, and downloads are all mounted below `/api`.

## Setup on Windows

```powershell
python -m venv backend\venv
.\backend\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
```

Set at least `JWT_SECRET_KEY` in `backend/.env`.

## Run

From the project root:

```powershell
npm run dev:backend
npm run dev:frontend
```

For the default local Celery setup, make sure Redis is running, then start the frontend, backend, and Celery worker together:

```powershell
npm run dev:all
```

You can also start the worker separately with `npm run dev:worker`. If `COMPOSER_REMOTE_API_URL` is configured, the backend can delegate generation to that remote service instead of relying on the local worker.

The frontend Vite server runs on port 8080 and proxies `/api` to the unified FastAPI backend on port 8000. There is no separate planner server on port 8001.

Generation architecture:
- `/api/generate` is the frontend-facing endpoint and persists generation history.
- By default it delegates Moonbeam work to Celery (`COMPOSER_EXECUTION_MODE=celery`) so the FastAPI process does not load the model.
- Set `COMPOSER_REMOTE_API_URL` to delegate to a remote composer service; this takes priority over local Celery.
- `COMPOSER_EXECUTION_MODE=direct` is available only as an explicit development fallback.

## Main endpoints

- `GET /api/health`
- `POST /api/auth/login`
- `GET /api/users/me`
- `GET /api/admin/me`
- `POST /api/generate`
- `GET /api/generations`
- `GET /api/generations/{id}/download/midi`
- `GET /api/generations/{id}/download/audio`
- `POST /api/composer/generate`
- `GET /api/composer/status/{celery_task_id}`
- `GET /api/composer/download/{file_name}`

## Runtime folders

- `backend/data/` stores SQLite data.
- `backend/generated/` stores legacy/generated MIDI and WAV outputs.
- `backend/composer_outputs/` stores Moonbeam composer outputs.

## Tests

```powershell
.\backend\venv\Scripts\python.exe -m pytest backend\tests
```
