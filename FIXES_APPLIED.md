# Integration fixes applied

This build repairs the frontend/backend integration issues found in the uploaded project.

## Fixed

1. User session validation now calls `GET /api/users/me` instead of the nonexistent `/api/auth/me`.
2. Admin session validation now calls `GET /api/admin/me` instead of the nonexistent `/api/auth/admin/me`.
3. The frontend no longer defaults to a planner server on port `8001`; planner/generation URL handling now uses the unified `/api` backend.
4. `/api/generate` is now the frontend-facing orchestration endpoint while Moonbeam execution is delegated outside the FastAPI process by default:
   - `COMPOSER_REMOTE_API_URL` if configured, otherwise
   - Celery/Redis with `COMPOSER_EXECUTION_MODE=celery`, or
   - explicit `COMPOSER_EXECUTION_MODE=direct` only as a development fallback.
5. Celery failures now become real `FAILURE` results instead of being swallowed with `Ignore`.
6. Composer status responses now return correct `/api/composer/download/...` URLs.
7. Generation records no longer expose filesystem paths to the browser. The API returns protected routes such as `/api/generations/{id}/download/midi`.
8. MIDI/audio download endpoints now verify ownership (admins may access all generations), locate legacy/current local outputs, and proxy remote composer files when necessary.
9. Generation history returns working protected download URLs for existing records.
10. Generated-file cleanup now supports both `backend/generated` and `backend/composer_outputs`.
11. The missing admin generation-analysis route was added: `GET /api/admin/generations/{id}/analysis`.
12. Admin research dashboard GET endpoints now return a valid empty state instead of 404 when no training data has been imported.
13. The missing `coherence_scores` SQLite table is now initialized.
14. `GenerationPage.tsx` had a malformed `formatTime()` function; it has been corrected.
15. Old `dev:planner`, `dev:audio`, port `8001`, and port `7860` startup instructions were removed from active scripts/UI/docs; `dev:worker` now starts the Celery worker used by the unified generation flow.
16. The composer output directory is created during FastAPI startup.

## Local configuration

For the normal worker setup, keep:

```env
COMPOSER_EXECUTION_MODE=celery
REDIS_URL=redis://localhost:6379/0
```

For a remote composer/Kaggle tunnel, configure:

```env
COMPOSER_REMOTE_API_URL=https://your-composer-host.example.com
```

When `COMPOSER_REMOTE_API_URL` is set, it takes priority over local Celery execution.

## Validation performed

- All backend Python source files compile successfully.
- All modified TypeScript/TSX files pass TypeScript syntax transpilation.
- SQLite generation initialization was checked and creates `generations`, `generation_analysis`, and `coherence_scores`.
- A full `npm run build` could not be executed in the analysis environment because the package registry available there did not contain one locked dependency (`zustand@5.0.11`).
- Full pytest collection could not run in the analysis environment because `pwdlib`/Celery packages were not available there. The project requirements already list those runtime dependencies.

## Blueprint + MIDI continuation follow-up

17. Prompt generation now persists the composer blueprint path in `generation_analysis.blueprint_file_path` and exposes a protected `blueprintFilePath` download URL alongside MIDI/audio.
18. `GET /api/generations/{id}/download/blueprint` now serves local blueprint JSON files or proxies remote composer blueprints with the same ownership checks used for MIDI/audio.
19. The generation result page now shows **Download Blueprint JSON** when the composer produced a blueprint.
20. Generation history now includes a **Blueprint** download button, so the plan remains downloadable after leaving the result page.
21. The MIDI Composer page is no longer a timer/static-sample demo. It uploads the selected `.mid/.midi` file to `POST /api/composer/continue-midi` and waits for the real backend result.
22. MIDI continuation now parses the uploaded MIDI (tempo, tracks, note range, note density, dominant/ending notes), uses that context to request a continuation from the existing Moonbeam composer, and appends the generated part after the source MIDI.
23. MIDI continuation returns the real combined MIDI file plus the continuation blueprint. The old hardcoded `/samples/completed_orchestration.mid` download has been removed.
24. `mido==1.3.3` was added as the lightweight MIDI parser/writer dependency.

### Continuation implementation note

The Moonbeam integration currently exposed by this repository is text-conditioned (`prompt -> blueprint -> MIDI`); it does not expose a native raw-MIDI-prefix conditioning API. The implemented continuation therefore analyzes the uploaded MIDI into musical context, conditions the existing composer with that context, and concatenates the generated next section to the source. This is a real end-to-end MIDI continuation workflow, but a future model API that accepts MIDI tokens/prefixes directly would provide stronger note-level continuity.

### Additional validation

- Backend Python sources compile after the blueprint/continuation changes.
- SQLite migration adds `generation_analysis.blueprint_file_path` to existing databases without recreating the table.
- A synthetic MIDI test verified source parsing, 120 BPM detection, note extraction, tick-resolution conversion, and appending the generated continuation after the original fragment.
- Frontend TypeScript parsing reported no syntax errors in the modified TSX; full project type/build verification still requires installing the repository's npm dependencies.
