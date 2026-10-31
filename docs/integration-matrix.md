# Integration Matrix — External Services & APIs

This document establishes the technical parameters, authentication requirements, rate limits, and verification status for all integrated external systems.

| Integration | Purpose | Auth Mechanism | Endpoints / Specs | Credentials Required | Verified In Workspace |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Threads Public Relay & GraphQL** | Crawl original post & comments | HTTP Session / CSRF Cookie / Relay cache parsing | `https://www.threads.net/@user/post/ID`<br>`https://www.threads.net/api/graphql` | None (Public) | **YES** (Direct verification on real Threads URLs) |
| **Edge TTS (Microsoft)** | Vietnamese voice synthesis | None (Secure WebSocket protocol) | `edge-tts` python protocol | None (Free) | **YES** (`vi-VN-HoaiMyNeural`, `vi-VN-NamMinhNeural` verified) |
| **FPT.AI Speech** | Northern, Central, Southern VN accents | API Key header (`api_key: ...`) | `https://api.fpt.ai/hmi/tts/v5` | `FPTAI_API_KEY` | Adapter configured with test fixtures |
| **Google Cloud TTS** | Vietnamese Wavenet synthesis | Service Account JSON / Google API Key | `texttospeech.googleapis.com/v1` | `GOOGLE_APPLICATION_CREDENTIALS` | Adapter configured with test fixtures |
| **CapCut Desktop Engine** | Multi-track timeline generation | Local filesystem IPC | Windows `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft` | None (Local software) | **YES** (Verified on host CapCut Desktop installation) |
| **FFmpeg Rendering Engine** | Card compositing, ducking & MP4 | Local CLI subprocessing | System path `ffmpeg.exe` (v8.1.1) | None (Local binary) | **YES** (Verified FFmpeg 8.1.1 full build) |
| **YouTube Data API v3** | Publish YouTube Shorts | OAuth 2.0 (`youtube.upload` scope) | `https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable` | Client ID & Client Secret | Adapter implemented with resumable upload protocol |
| **Meta Graph API v19+** | Publish Facebook Page Reels | Page Access Token (`pages_manage_posts`, `pages_read_engagement`) | `https://graph.facebook.com/v19.0/{page-id}/video_reels` | Page Token & Page ID | Adapter implemented with chunked upload workflow |
| **TikTok Content Posting API** | Direct Video Post | OAuth 2.0 (`video.publish`, `video.upload`) | `https://open.tiktokapis.com/v2/post/publish/video/init/` | Client Key & Client Secret | Adapter implemented with video chunk transfer protocol |
