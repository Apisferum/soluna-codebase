# Synestra Unified Backend

This project uses a single FastAPI application (`app.main:app`) on port **8000**. Authentication, generation, admin, audio analysis, stem separation, WebSocket, and composer routers are integrated into this application.

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

Open Swagger at `http://127.0.0.1:8000/docs`. The frontend should use `/api` (or `VITE_API_URL=http://127.0.0.1:8000`) and must not call a separate port 8001 planner service.
