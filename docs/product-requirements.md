# Threads Comment Video Studio — Product Requirements Document (PRD)

## 1. Executive Summary
**Threads Comment Video Studio** is a local-first desktop application designed for digital creators, social media marketers, and community builders. It transforms public Threads conversations into engaging 9:16 vertical short-form videos with synchronized Vietnamese text-to-speech voiceovers and generates an editable CapCut Desktop project file alongside a finished MP4. Users can publish directly to YouTube Shorts, Facebook Page Reels, and TikTok.

---

## 2. Core Value Proposition & Workflow
```
[ Threads URL ] 
      │
      ▼
[ Post & Nested Comments Extraction ]
      │
      ▼
[ Selection & Content/TTS Editor ]
      │
      ▼
[ Vietnamese Voice Studio (Edge TTS / FPT.AI / Google Cloud) ]
      │
      ▼
[ Video Composer (Minecraft 9:16 Background + Card Layout + Audio Sync) ]
      │
      ├──────────────────────────────┬──────────────────────────────┐
      ▼                              ▼                              ▼
[ Finished MP4 Video ]      [ CapCut Project Package ]      [ Social Media Publishing ]
                             (Multi-track: V1-V3, A1-A2)     (YouTube Shorts, FB Reels, TikTok)
```

---

## 3. Product Scope

### In-Scope (MVP)
1. **Threads Crawler Module**:
   - URL parsing (`threads.net/@username/post/POST_ID` & `threads.com`).
   - Original post retrieval (post ID, author username, display name, avatar, text, media references, like/reply counts, timestamp).
   - Comment and nested reply extraction preserving thread hierarchy.
   - Resilient multi-provider architecture: Public Relay Stream Cache Parser, GraphQL pagination query engine, and Playwright fallback.
2. **Comment Management Module**:
   - Engagement sorting (likes, replies, publication time).
   - Top-N automated selection, manual checkboxes, drag-and-drop reordering.
   - Dual-text editing: **Display Text** (shown on video card) vs **TTS Text** (read aloud by voice synthesizer).
   - Original crawled data preservation with 1-click restore.
3. **Vietnamese TTS Studio**:
   - Multi-provider: Edge TTS (zero-credential neural voices `vi-VN-HoaiMyNeural` and `vi-VN-NamMinhNeural`), FPT.AI Speech, Google Cloud Text-to-Speech.
   - Voice preview, speed adjustment (0.5x – 2.0x), volume control.
   - Global default voice with per-comment voice overrides.
   - Deterministic audio caching by MD5(provider, voice, speed, text).
4. **Video Composer (FFmpeg Engine)**:
   - 9:16 vertical video layout (1080x1920 @ 30fps).
   - Minecraft gameplay background video selection (trimming, looping, volume control).
   - High-fidelity styled card generation for original post and comment scenes.
   - Scene timeline computation with audio duration synchronization, min reading time, and speech pauses.
   - Background music with optional ducking during voiceovers.
5. **CapCut Desktop Project Exporter**:
   - Native CapCut Desktop draft generation via `pycapcut`.
   - Discrete timeline tracks:
     - `V1`: Minecraft background video.
     - `V2`: Original Threads post card image.
     - `V3`: Comment card images.
     - `A1`: TTS voiceover audio clips.
     - `A2`: Background music audio track.
     - `V4`: Optional watermark.
   - Windows CapCut Desktop draft metadata patcher (`draft_content.json` and `draft_meta_info.json`).
   - Standalone export package with bundled assets and import helper script for cross-machine handoff.
6. **Social Media Publisher**:
   - YouTube Shorts (YouTube Data API v3, resumable upload, title, description, privacy).
   - Facebook Page Reels (Meta Graph API v19+, Page Access Token, resumable Reels upload).
   - TikTok (TikTok Content Posting API, creator info, direct post).
   - Multi-platform publishing center with credential management and explicit confirmation.
7. **Local Project & Asset Management**:
   - SQLite database for projects, posts, comments, selections, audio assets, render jobs, and publishing history.
   - Asset library for background videos, music tracks, and generated exports.

### Excluded from MVP
- Autonomous AI generation/downloading of Minecraft gameplay footage.
- AI meme generation or external meme libraries.
- Heavy manual video editor replicating CapCut's desktop GUI.
- Cloud SaaS hosting or multi-tenant user accounts.
- Personal Facebook profile video publishing (Graph API restriction).

---

## 4. User Personas & Core User Stories
1. **Short-form Content Creator**:
   - *Goal*: Quickly produce 3–5 daily viral TikTok/Reels/Shorts from trending Threads discussions.
   - *Requirement*: Paste a link, pick top 5 comments, customize speaking speed, render in under 60 seconds, and get both an MP4 and a CapCut draft for fine-tuning.
2. **Vietnamese Community Admin**:
   - *Goal*: Repackage community discussions into engaging video format with natural Vietnamese voiceovers.
   - *Requirement*: Edit abbreviations, slang, or emojis in TTS text while keeping original display text intact.
