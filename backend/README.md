# Backend services

The backend is split into three independent FastAPI services.

## Services

| Service | Module | Port | Purpose |
|---|---|---:|---|
| Auth API | `services.auth_api.main:app` | 8000 | Users, JWT authentication, admin endpoints and history |
| Planner API | `services.planner_api.main:app` | 8001 | Prompt planning, MIDI generation and WAV rendering |
| Audio API | `services.audio_api.main:app` | 7860 | Chord analysis, audio separation and YouTube processing |

## Setup on Windows

```powershell
python -m venv backend\venv
.\backend\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

Create `backend/.env` from `backend/.env.example` and set at least `JWT_SECRET_KEY`.

## Run services separately

Run these from the project root:

```powershell
npm run dev:auth
npm run dev:planner
npm run dev:audio
```

Or run the frontend and all backend services together:

```powershell
npm run dev:all
```

## Runtime folders

- `backend/data/` stores SQLite data.
- `backend/generated/` stores generated MIDI and WAV files.
- Both folders are ignored by Git except for `.gitkeep`.

## Tests

```powershell
.\backend\venv\Scripts\python.exe -m pytest backend\tests
```
