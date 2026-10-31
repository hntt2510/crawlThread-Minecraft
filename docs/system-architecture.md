# System Architecture — Threads Comment Video Studio

## 1. High-Level Architecture Overview

Threads Comment Video Studio follows a local-first client-server pattern optimized for Windows 10/11:

```
┌─────────────────────────────────────────────────────────────┐
│                       Browser Frontend                      │
│        React 18 + Vite + TypeScript + Tailwind CSS          │
│            TanStack Query + Lucide Icons + Router           │
└──────────────────────────────▲──────────────────────────────┘
                               │ HTTP / REST / JSON
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Backend (Python)                 │
│  - REST API Routers (/api/projects, /api/threads, ...)      │
│  - Job Manager & Async Task Orchestrator                   │
│  - SQLAlchemy 2.0 ORM + Alembic Migrations                  │
│  - File System Asset Storage Engine                         │
└───────┬──────────────┬──────────────┬──────────────┬────────┘
        │              │              │              │
        ▼              ▼              ▼              ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│Threads Engine││  TTS Engine  ││FFmpeg Engine ││CapCut Builder│
│- Relay Cache ││- Edge TTS    ││- Image Render││- pycapcut    │
│- GraphQL API ││- FPT.AI      ││- Video Comp  ││- Meta Patcher│
│- Scraper Core││- Google TTS  ││- Audio Duck  ││- Package Zip │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘
        │              │              │              │
        ▼              ▼              ▼              ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│Local SQLite  ││Audio Cache   ││Export Storage││CapCut Desktop│
│  database    ││  (wav/mp3)   ││   (1080x1920)││Draft Folder  │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘
```

---

## 2. Component Specifications

### 2.1 Backend Core (FastAPI & Python 3.12)
- **Framework**: FastAPI with asynchronous route handlers and Pydantic v2 schemas.
- **Database**: SQLite with Write-Ahead Logging (`PRAGMA journal_mode=WAL`) managed via SQLAlchemy 2.0 and Alembic.
- **Background Worker**: In-process persistent thread pool executor managing long-running crawl, synthesis, rendering, and publishing tasks with database state persistence, retry policies, and granular progress reporting.
- **Asset Directory**: Structured local directory (`./data/projects/<project_id>/assets/`, `audio/`, `renders/`, `capcut/`).

### 2.2 Threads Crawling Subsystem
- **Provider Architecture**:
  1. `RelayStreamCrawler`: High-speed parser extracting server-rendered GraphQL graph data from `<script data-sjs>` tags (validated via direct HTTP session with CSRF cookie).
  2. `ThreadsGraphQLCrawler`: Executes Meta's internal GraphQL endpoints using dynamic doc IDs and pagination cursors.
  3. `PlaywrightCrawler` (Optional Fallback): Headless browser session for edge cases with dynamic CAPTCHAs.
- **Data Normalizer**: Maps raw Threads objects into standardized `Post` and hierarchical `Comment` schemas.

### 2.3 Vietnamese TTS Studio Subsystem
- **Provider Interface**: Abstract `TTSProvider` with `synthesize(text, voice, rate, pitch) -> AudioResult`.
- **Implementations**:
  - `EdgeTTSProvider`: Built-in Microsoft Neural TTS with Vietnamese voices (`vi-VN-HoaiMyNeural`, `vi-VN-NamMinhNeural`). Free, fast, zero configuration.
  - `FPTAISpeechProvider`: Enterprise Vietnamese TTS with BanMai, ThuMinh, MyAn, GiaHuy voices.
  - `GoogleTTSProvider`: Google Cloud Text-to-Speech standard and Wavenet Vietnamese voices.
- **Caching Layer**: Deterministic SHA256 hashed filenames based on `(provider, voice, rate, volume, text)` stored in `./data/cache/audio/`.

### 2.4 Video Rendering Subsystem (FFmpeg + Card Generator)
- **Visual Card Generator**: Renders pixel-perfect 9:16 post cards and comment cards using Pillow (PIL) or headless SVG rasterization with Vietnamese Unicode fonts (Roboto / Inter).
- **Timeline Engine**:
  - Calculates per-scene durations: $\text{Duration} = \max(\text{audio\_duration} + \text{pause\_buffer}, \text{min\_reading\_time})$.
  - Assembles complex filter graphs in FFmpeg:
    - Scales and crops Minecraft gameplay to 1080x1920.
    - Overlays post cards and comment cards with smooth fade transitions.
    - Mixes TTS voiceover tracks at primary volume with background music ducked by -14dB during speech.
- **Encoding Profile**: H.264 (libx264, preset `fast`, crf 20), AAC audio (192kbps, 44.1kHz), 30fps MP4.

### 2.5 CapCut Desktop Exporter Subsystem
- **Builder**: Wraps `pycapcut` with a multi-track timeline construction:
  - V1: Background video clips.
  - V2: Post card image segment.
  - V3: Comment card image segments synchronized to speech cue points.
  - A1: Voiceover TTS audio segments.
  - A2: Background music audio segment.
- **Desktop Draft Integrator**: Patches `draft_content.json` and `draft_meta_info.json` with unique project UUIDs and copies directly to `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\<Project_Name>\`.
- **Standalone Exporter**: Zips the draft folder and all referenced assets with a `capcut_import.py` script so other Windows machines can import it with 1 click.

### 2.6 Social Media Publishing Subsystem
- **YouTube Shorts**: YouTube Data API v3 resumable chunked upload endpoint (`/upload/youtube/v3/videos`).
- **Facebook Reels**: Meta Graph API v19+ Page video endpoint with `upload_phase=start`, `transfer`, `finish` and `publish` steps.
- **TikTok**: TikTok Content Posting API with creator info verification and direct video upload workflow.
