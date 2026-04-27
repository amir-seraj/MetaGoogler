# Meta-Googler v2 — Design Spec

**Date:** 2026-04-27
**Status:** Approved (brainstorming complete, awaiting user review of spec)
**Supersedes:** the existing CustomTkinter desktop GUI and the React Native mobile app.

---

## 1. Overview

**Meta-Googler v2** is a localhost web app for bulk-fixing music metadata in a personal library of 500–5,000 audio files.

A user drops a folder into the app. The app extracts a 7-second sample from the middle of each track, fingerprints it via AudD/AcoustID, and proposes corrected tags. For files the fingerprint cannot match, an LLM proposes plausible tags from filename, duration, and any partial existing tags. The user triages the proposals — spreadsheet-style multi-select for surgical edits, keyboard-driven card-by-card for low-confidence cases — and clicks apply. The app writes tags, optionally renames files, optionally embeds cover art, and writes a `.metaorig/` snapshot for rollback.

The CustomTkinter desktop GUI, the React Native mobile app, and the web variants (`AppWeb`, `AppWebInteractive`, `AppDebug`) are deleted as part of this work.

## 2. Goals & non-goals

### Goals

- One UX surface (web frontend served from localhost), one job (bulk metadata fixing).
- Reuse the working Python pipeline: AudD song identification, LiteLLM AI suggestions, mutagen tag writing, cover art fetching.
- Survive an AI-suggestion-gone-wrong without data loss (auto-backup).
- Fast enough that a 5,000-file scan is usable interactively (streaming progress, no blocking modals).
- Visually modern; behaves like a 2026 web app, not a 2010 desktop dialog.

### Non-goals

- Music playback / player.
- Playlists or library browsing for entertainment.
- Multi-folder / nested-folder workflows in v1.
- User accounts, multi-user, or cloud sync.
- MCP server integration (Phase 2 of the prior roadmap — separate spec later).
- Mobile / tablet UI (responsive enough not to break; not designed for touch).
- Internationalization.
- Auto-update or installers beyond `pip install`.
- Editing audio data itself (cuts, normalization, format conversion).

## 3. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Browser (Chrome/Firefox) — http://localhost:<port>          │
│  React + Vite + Tailwind + shadcn/ui                        │
│  Views: Setup, Scanning, Library, Triage, Apply, Settings   │
└──────────────┬──────────────────────────────────────────────┘
               │ REST + WebSocket
┌──────────────▼──────────────────────────────────────────────┐
│ FastAPI (Python) — launched by `meta-googler` CLI            │
│  Routes: /scan, /queue, /accept, /reject, /apply, /settings │
│  WebSocket: streams scan + apply progress                    │
│                                                              │
│  Reuses existing Python modules:                             │
│  ├─ song_identifier.py    (AudD/AcoustID)                   │
│  ├─ ai_manager_v2.py      (LiteLLM)                         │
│  ├─ cover_art_fetcher.py  (cover art)                       │
│  ├─ song_metadata_fixer_v2.py (mutagen tag I/O — trimmed)   │
│                                                              │
│  New modules:                                                │
│  ├─ api/app.py            (FastAPI wiring, static serve)    │
│  ├─ api/jobs.py           (in-memory job state)             │
│  ├─ api/backup.py         (.metaorig/ manager)              │
│  └─ api/sampler.py        (7-sec extractor wrapper)         │
└─────────────────────────────────────────────────────────────┘
```

### Key choices

- **Frontend stack:** React 18 + Vite + Tailwind CSS + shadcn/ui. Chosen for visual freedom (shadcn copies components in, no vendor lock-in), familiarity (existing mobile work was React), and clean fit with FastAPI as a JSON+WebSocket backend.
- **No database.** State lives in memory inside the FastAPI process. A scan/triage/apply session is one job; if the process dies, the user re-scans. Justified by the 500–5,000 file scale and the single-folder-at-a-time workflow.
- **Process model:** the `meta-googler` CLI picks a free port, starts FastAPI in the foreground, opens the browser to `http://localhost:<port>`, and blocks until Ctrl-C or the user closes the browser tab and the server's idle-timeout fires.
- **Distribution:** `pip install meta-googler` ships both the Python backend and the pre-built JS bundle (Vite output committed to `src/api/static/` at release time, served by FastAPI's static handler). No Node.js required at runtime.
- **Dev workflow:** during development, Vite's dev server runs separately on its own port and proxies API calls to FastAPI. FastAPI serves the bundled static directory only in production / installed mode.
- **Concurrency model:** at most one active scan job and one active apply job at any time. The `job_id` returned by `POST /scan` and `POST /apply` exists solely so a reconnecting WebSocket client can correlate streamed events with the request it issued; the server itself holds only the *current* job.

## 4. UI views

### View map

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  1. SETUP        │ ──► │  2. SCANNING     │ ──► │  3. LIBRARY      │
│  Drop folder     │     │  Live progress   │     │  Spreadsheet     │
│  + options       │     │  (WS stream)     │     │  Sortable,       │
│                  │     │                  │     │  filterable      │
└──────────────────┘     └──────────────────┘     └────────┬─────────┘
                                                            │
                                                            ▼
                         ┌──────────────────┐     ┌──────────────────┐
                         │  5. APPLY        │ ◄── │  4. TRIAGE       │
                         │  Write progress  │     │  Card-by-card    │
                         │  Done / errors   │     │  Keyboard-driven │
                         │  Roll-back btn   │     │  for low-conf    │
                         └──────────────────┘     └──────────────────┘

       (Settings drawer accessible from any view via top-bar gear)
```

### 4.1 Setup

- Big drop zone (drag a folder or click to pick).
- Three checkboxes:
  - "Auto-rename files to `Artist - Title.ext`" (default: on)
  - "Fetch missing cover art" (default: on)
  - "Skip files with already-complete tags" (default: off). *Complete = non-empty title, artist, and album.*
- Single CTA: **Start scan**.

### 4.2 Scanning

- Top: progress bar `X of Y fingerprinted` with ETA.
- Live counters: `matched / unmatched / failed`.
- Bottom: tail-log of the last ~10 completed files (filename + result).
- Top-right: **Skip to library** button (enabled at ≥80% complete) so user doesn't wait on stragglers.

### 4.3 Library — primary working surface

Virtualized table. One row per file. Columns:

| Column | Notes |
|---|---|
| File | basename |
| Title (current) | from existing tag |
| Title (proposed) | diff-highlighted vs current |
| Artist (current / proposed) | same pattern |
| Album (current / proposed) | same |
| Confidence | `high` (fingerprint match), `med` (LLM proposed and self-reported confident), `low` (LLM proposed and self-reported uncertain), `none` (no proposal — neither fingerprint nor LLM produced a result). Exact thresholds chosen during implementation. |
| Status | `pending`, `accepted`, `rejected`, `applied`, `failed` |

Behavior:

- Sort + filter on every column.
- Top-bar filter chips: **Low confidence**, **Unmatched**, **Missing artwork**, **Missing genre**.
- Multi-select rows → bulk actions: **Accept proposed**, **Reject**, **Send to triage**, **Edit field across selected**.
- Row click expands inline to a detail strip: full tag diff, current cover, proposed cover, `Edit` button.
- Top-right buttons: **Triage low-confidence** (jumps to view 4 with low-conf filter pre-applied), **Apply N accepted** (jumps to view 5).

### 4.4 Triage queue

Full-screen card. One file at a time.

- Left half: current state — filename, current tags, embedded cover (if any).
- Right half: proposed state — proposed tags (editable in place), fetched cover art.
- Diff lines highlighted (added/changed in green, removed in red).
- Source label, e.g.: *"Fingerprint match (AudD): 0.94 confidence"* or *"LLM suggestion (claude-opus-4-7): no fingerprint match."*
- Footer: keyboard shortcuts always visible — `J/K` next/prev, `A` accept, `R` reject, `E` edit, `S` skip, `Esc` back to library.
- Counter: `12 of 47 reviewed`.

### 4.5 Apply

- Confirmation: *"About to write tags to 38 files, rename 12, embed cover for 9. Backups to `<folder>/.metaorig/`. Proceed?"*
- Streaming progress (WebSocket).
- On done: *"38 succeeded, 0 failed."* with **Roll back all** and **Show in folder** buttons.

### 4.6 Settings (drawer)

- API keys (AudD, OpenAI, Anthropic, Google, etc.).
- Default LLM model.
- Backup directory (default: `<scanned-folder>/.metaorig/`).
- Default values for the three Setup checkboxes.

## 5. Data flow per file

```
file.mp3
  │
  ├─► extract 7s from middle (sampler.py)
  │       │
  │       ▼
  ├─► fingerprint (song_identifier.py → AudD / AcoustID)
  │       │
  │       ├─ matched   ──► tags from MusicBrainz/AudD ──► confidence: HIGH
  │       │
  │       └─ no match  ──► LLM proposal (ai_manager_v2.py)
  │                          using filename + duration + partial existing tags
  │                          ──► confidence: MED (or LOW if LLM uncertain)
  │
  ├─► (optional) fetch cover art if missing (cover_art_fetcher.py)
  │
  └─► proposal lands in queue (jobs.py state)
         │
         ▼
      user accepts / edits / rejects in Library or Triage view
         │
         ▼
      on Apply:
         backup original tags to <folder>/.metaorig/<filename>.json
         write new tags via mutagen
         optionally rename file
         optionally embed cover art
```

## 6. Module layout

### Deleted

| Path | Reason |
|---|---|
| `mobile_app/` (entire directory) | Mobile dropped — not the job-to-be-done. |
| `src/app_gui.py` (~997 lines) | CustomTkinter GUI replaced by web app. |
| `src/utils/suggestion_window.py` (~274 lines) | Tk popup, no longer used. |
| `src/batch_process.py` (~270 lines) | Subsumed into web app's apply flow. |
| `metadatafixer-gui.spec`, `metadatafixer_gui.spec`, `metadatafixer.spec` | PyInstaller specs for the deleted GUI. |
| `MOBILE_APP_SUMMARY.md`, `PHASE_1_SUMMARY.txt` | Obsolete narratives. |

### Survives, possibly trimmed

| Path | Action |
|---|---|
| `src/song_identifier.py` (~444 lines) | Keep as-is. |
| `src/ai_manager_v2.py` (~375 lines) | Keep. Will be invoked from the FastAPI route layer. |
| `src/utils/cover_art_fetcher.py` (~482 lines) | Keep. Wired into apply pipeline. |
| `src/song_metadata_fixer_v2.py` (~1,200 lines) | **Trim.** Today the file mixes UI logic, file I/O, mutagen calls, and validation. Extract pure functions: `read_tags`, `write_tags`, `validate_tags`. Drop the rest. Target ~400 lines. |
| `src/utils/config_manager.py`, `src/utils/logger_setup.py` | Keep. |
| `src/main.py` | Replace contents with the FastAPI launcher (CLI: pick port, start server, open browser, block). |

### New files

```
src/
  api/
    app.py                # FastAPI app, route wiring, CORS, static serve
    jobs.py               # in-memory job state (current scan, queue, settings)
    backup.py             # .metaorig/ snapshot + restore
    sampler.py            # thin wrapper exposing 7-sec extraction
    routes/
      __init__.py
      scan.py             # POST /scan, WebSocket /ws/scan
      queue.py            # GET /queue, POST /accept, POST /reject, PATCH /edit
      apply.py            # POST /apply, WebSocket /ws/apply, POST /rollback
      settings.py         # GET / PATCH /settings
    static/               # built JS bundle goes here at release time

frontend/                 # Vite project — NOT shipped in source distribution; builds into src/api/static/
  package.json
  vite.config.ts
  src/
    main.tsx
    App.tsx
    routes/
      Setup.tsx
      Scanning.tsx
      Library.tsx
      Triage.tsx
      Apply.tsx
    components/
      DropZone.tsx
      LibraryTable.tsx    # virtualized
      TriageCard.tsx
      ProgressBar.tsx
      SettingsDrawer.tsx
      DiffField.tsx
    api/
      client.ts           # fetch + WebSocket wrapper
      types.ts            # shared types mirroring backend pydantic models
    hooks/
      useScanStream.ts
      useApplyStream.ts
```

## 7. API surface (contract)

### REST

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/scan` | Body: `{folder: string, options: {auto_rename, fetch_cover, skip_complete}}`. Returns `{job_id}`. Triggers async scan. |
| `GET` | `/queue` | Returns the current job's queue: list of files with current tags, proposals, confidence, status. |
| `POST` | `/accept` | Body: `{file_ids: string[]}`. Marks files as accepted. |
| `POST` | `/reject` | Body: `{file_ids: string[]}`. Marks files as rejected. |
| `PATCH` | `/edit` | Body: `{file_id: string, fields: {title?, artist?, album?, ...}}`. Manual edits to a proposal. |
| `POST` | `/apply` | Body: `{}` (operates on the current job's accepted files). Returns `{job_id}`. |
| `POST` | `/rollback` | Body: `{}`. Restores from `.metaorig/`. |
| `GET` | `/settings` / `PATCH` | Read / update persistent settings (API keys, default toggles). |

### WebSocket

- `/ws/scan` — server pushes `{file_id, status, proposal?}` events as each file finishes fingerprinting / LLM proposal.
- `/ws/apply` — server pushes `{file_id, status, error?}` events as each file is written / renamed / cover-art-embedded.

## 8. Error handling

- **Scan errors per file** never abort the job. The file is marked `failed` with a reason; job continues.
- **AudD rate limit / network failure** → exponential backoff, then mark the file as "no fingerprint, fall back to LLM." LLM failure → mark `unmatched` with no proposal; surfaces in triage.
- **Apply errors per file** (mutagen write failure, permission denied, disk full) → file marked `apply-failed`, others continue, error surfaces in the Apply view's failure list.
- **Backup write failure** → apply for that file is **aborted before mutagen runs**. We never write tags without a backup. Error surfaces immediately.
- **FastAPI server crash** → user re-runs `meta-googler`, has to re-scan. Acceptable at scale B.
- **Browser disconnect mid-job** → server keeps running; user reopens browser, picks up where they left off (state lives in the FastAPI process).

## 9. Testing

- **Backend unit:** pytest on the pure functions — `read_tags`, `write_tags`, `validate_tags`, `backup`, `sampler`. Use a fixtures folder of small MP3s.
- **Backend integration:** pytest on `/scan` + `/apply` against the same fixtures, asserting the round-trip writes and the `.metaorig/` rollback restores the original.
- **Frontend unit:** Vitest on component logic (DiffField rendering, LibraryTable filter/sort behavior, keyboard handler in TriageCard).
- **End-to-end smoke:** one Playwright test — drop folder, scan completes, apply succeeds, files have new tags. Run in CI on the fixtures folder.
- **AI-suggestion quality** is not automated. Human judgment.

## 10. Out of scope (explicit guard against scope creep)

- Music playback / player.
- Playlists.
- Multi-folder / nested-folder workflows in v1.
- User accounts, multi-user, cloud sync.
- MCP servers (separate spec, later).
- Mobile / tablet UI.
- Internationalization.
- Auto-update or installers beyond `pip install`.
- Editing audio data (cuts, normalization, format conversion).
