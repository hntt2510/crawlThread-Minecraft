# API Specification — Threads Comment Video Studio

Base URL: `http://localhost:8000/api`

---

## 1. Projects API (`/api/projects`)

- `GET /api/projects`: List all projects with summaries, thumbnails, and statuses.
- `POST /api/projects`: Create a new project.
  ```json
  { "title": "Gaming Community Debate", "threads_url": "https://www.threads.net/@zuck/post/DeZgeQhm6RW" }
  ```
- `GET /api/projects/{id}`: Retrieve detailed project data including crawled post, comments, and current settings.
- `PATCH /api/projects/{id}`: Update project settings (background asset, volume, aspect ratio).
- `DELETE /api/projects/{id}`: Delete a project and associated temporary assets.

---

## 2. Threads Crawler API (`/api/threads`)

- `POST /api/threads/crawl`: Trigger an asynchronous crawl job for a Threads URL.
  ```json
  { "project_id": "uuid", "threads_url": "https://www.threads.net/@...", "max_comments": 50 }
  ```
  Returns: `{ "job_id": "job-uuid", "status": "processing" }`
- `GET /api/threads/crawl/{job_id}`: Poll crawl job progress, statistics (total found, replies, rate status).

---

## 3. Comments API (`/api/comments`)

- `GET /api/projects/{project_id}/comments`: Get all crawled comments with hierarchy tree and metrics.
- `POST /api/projects/{project_id}/selections`: Update selected comments, custom order, and texts.
  ```json
  {
    "selections": [
      {
        "comment_id": "4017996599141669939",
        "sequence_order": 0,
        "display_text": "Can’t wait to tear this up 🤤",
        "tts_text": "Không thể chờ đợi để thưởng thức món này nữa rồi!",
        "voice_id": "vi-VN-NamMinhNeural",
        "voice_rate": 1.05
      }
    ]
  }
  ```
- `POST /api/projects/{project_id}/comments/restore/{comment_id}`: Revert custom edits back to crawled original.

---

## 4. TTS Studio API (`/api/tts`)

- `GET /api/tts/voices`: List available voices grouped by provider and accent.
- `POST /api/tts/preview`: Synthesize a quick live preview audio snippet.
  ```json
  { "provider": "edge_tts", "voice": "vi-VN-HoaiMyNeural", "text": "Xin chào các bạn!", "rate": 1.0 }
  ```
- `POST /api/tts/generate/{project_id}`: Trigger asynchronous batch voice generation for all selected comments.
- `GET /api/tts/status/{job_id}`: Check voice generation progress.

---

## 5. Media & Assets API (`/api/media`)

- `GET /api/media`: List local Minecraft background videos and music tracks.
- `POST /api/media/upload`: Upload a local background video or audio file.
- `GET /api/media/{id}/stream`: Stream local video or audio for preview playback.

---

## 6. Video Composer & Render API (`/api/render`)

- `POST /api/render/start`: Trigger FFmpeg video rendering job.
  ```json
  {
    "project_id": "uuid",
    "background_asset_id": "media-uuid",
    "background_start_sec": 10.5,
    "background_volume": 0.25,
    "voice_volume": 1.0,
    "resolution": "1080x1920",
    "fps": 30
  }
  ```
- `GET /api/render/status/{job_id}`: Check render progress percentage, frame rate, and logs.
- `GET /api/render/download/{project_id}`: Download finalized MP4 video.

---

## 7. CapCut Exporter API (`/api/capcut`)

- `POST /api/capcut/export`: Generate CapCut Desktop draft and export package.
  ```json
  {
    "project_id": "uuid",
    "install_to_local_capcut": true
  }
  ```
- `GET /api/capcut/download/{project_id}`: Download zip package containing draft and all bundled assets.

---

## 8. Social Media Publishing API (`/api/publishing`)

- `GET /api/publishing/accounts`: Get connected social accounts (YouTube, Facebook Pages, TikTok).
- `POST /api/publishing/connect/{platform}`: Initiate OAuth / Token setup flow.
- `POST /api/publishing/publish`: Publish a rendered video to chosen platforms with explicit confirmation.
  ```json
  {
    "project_id": "uuid",
    "platforms": ["youtube", "facebook", "tiktok"],
    "youtube_metadata": { "title": "Hài hước Threads", "description": "#Shorts #Threads", "privacy": "public" },
    "facebook_metadata": { "page_id": "page-123", "caption": "Bình luận Threads vui nhộn" },
    "tiktok_metadata": { "caption": "Xem hết để thấy bất ngờ #trending", "privacy": "PUBLIC_TO_EVERYONE" }
  }
  ```
- `GET /api/publishing/jobs/{job_id}`: Monitor publish status and retrieve published URLs.
