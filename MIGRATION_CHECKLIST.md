# Migration checklist

Use the reorganised project as a new working copy first. Do not overwrite your current project until it starts successfully.

## 1. Back up the current project

```powershell
cd D:\daisy\music_frontend
git add .
git commit -m "Backup before project reorganisation"
```

## 2. Extract the reorganised project beside the current project

Example destination:

```text
D:\daisy\music_frontend_reorganised
```

## 3. Restore private environment values

Do not copy `.env` files into Git. Create the following locally as needed:

```text
.env.local
backend\.env
```

Use the included `.env.example` files as templates.

## 4. Move the existing database

The new default database path is:

```text
backend\data\synestra.db
```

Copy the old database:

```powershell
Copy-Item `
  D:\daisy\music_frontend\backend\auth_backend\synestra.db `
  D:\daisy\music_frontend_reorganised\backend\data\synestra.db
```

Skip this step when you want a new empty database.

## 5. Recreate dependencies

```powershell
cd D:\daisy\music_frontend_reorganised
npm install

python -m venv backend\venv
.\backend\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

Do not copy the old `node_modules` or `backend\venv` folders.

## 6. Start the complete project

```powershell
npm run dev:all
```

Expected local services:

```text
Frontend     http://localhost:8080
Auth API     http://localhost:8000
Planner API  http://localhost:8001
Audio API    http://localhost:7860
```

## 7. Verify before replacing the old project

Check:

- Registration and login
- Admin login and dashboard
- Music generation
- Generation history
- Chord analysis
- MIDI and WAV download
- Frontend navigation and static assets

Only replace the old project after these checks pass.
