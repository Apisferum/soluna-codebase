# Reorganised project structure

This version separates frontend application concerns and Python services without changing the user-facing routes.

```text
music_frontend/
├── src/
│   ├── app/                  # App shell and route guards
│   ├── pages/
│   │   ├── home/             # Landing page
│   │   ├── auth/             # Login, register, password reset
│   │   ├── admin/            # Admin login and dashboard
│   │   ├── ai/               # Generation, history, chord AI, separation
│   │   ├── tools/            # Music learning and composition tools
│   │   ├── blog/             # Blog pages
│   │   └── system/           # 404 and system pages
│   ├── components/
│   │   ├── common/           # Cross-feature reusable components
│   │   ├── layout/           # Navigation, footer and global menu
│   │   ├── music/            # Chord, fretboard, piano and audio UI
│   │   └── ui/               # Low-level design-system primitives
│   ├── services/api/         # HTTP API clients
│   ├── contexts/             # React context providers
│   ├── hooks/                # Shared React hooks
│   ├── stores/               # Zustand stores
│   ├── lib/                  # Browser/audio domain utilities
│   ├── types/                # Shared TypeScript models
│   ├── data/                 # Static application data
│   └── analytics/            # GA4 and PostHog integration
├── backend/
│   ├── services/
│   │   ├── auth_api/         # Authentication, users and admin API
│   │   ├── planner_api/      # Prompt planning and MIDI/audio generation
│   │   └── audio_api/        # Chord analysis, separation and YouTube audio
│   ├── scripts/              # Maintenance and setup scripts
│   ├── tests/                # Backend tests
│   ├── requirements/         # Service-specific Python dependencies
│   ├── data/                 # SQLite/runtime data (gitignored)
│   ├── generated/            # Generated MIDI/WAV files (gitignored)
│   ├── archive/              # Old source snapshots, not runtime code
│   └── docs/                 # Backend documentation
├── public/                   # Static browser assets
├── docs/                     # Project documentation
└── scripts/                  # Frontend/build scripts
```

## Local commands

```powershell
npm install
python -m venv backend\venv
.\backend\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
npm run dev:all
```

Services:
- Frontend: `http://localhost:8080`
- Unified FastAPI backend: `http://localhost:8000`
- All backend HTTP routes are served below `/api`.

## Existing database migration

The reorganised auth service stores SQLite data at `backend/data/synestra.db`. Copy your existing database before starting the auth service:

```powershell
Copy-Item .\backend\auth_backend\synestra.db .\backend\data\synestra.db
```

Alternatively set `SYNESTRA_DB_PATH` to the old database location.
