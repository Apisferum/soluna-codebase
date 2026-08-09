# Synestra Unified Backend Baseline

This branch contains only the shared FastAPI baseline. It does not yet
migrate authentication, planner, or audio functionality.

## Run on Windows PowerShell

```powershell
cd backend

python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

Copy-Item .env.example .env

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

- API root: http://127.0.0.1:8000/api/
- Health: http://127.0.0.1:8000/api/health
- Swagger: http://127.0.0.1:8000/docs

## Run tests

```powershell
pytest
```

## Team integration rule

Service branches should add `APIRouter` objects. They must not create
another `FastAPI()` object or another Uvicorn entry point.

Each team member should normally edit their own route, schema, service,
and repository files. The baseline owner should control central changes
to `app/main.py`, `app/api/router.py`, shared configuration, middleware,
and lifespan startup.
