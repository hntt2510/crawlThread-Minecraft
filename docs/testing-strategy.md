# Testing Strategy & Quality Assurance Plan

## 1. Quality Objectives & Test Levels
The application must pass strict automated and integration checks before delivery:
1. **Unit Tests (Backend)**: Verify data models, normalization logic, text sanitizer, duration calculator, and configuration validators using `pytest`.
2. **Integration Tests (Crawling & TTS)**:
   - Threads Relay and regex parsing with fixture HTML and live URL integration tests.
   - Vietnamese Edge TTS audio synthesis and file persistence verification.
3. **Video Pipeline Tests (FFmpeg)**:
   - Card image generation with Vietnamese characters and emoji fallback.
   - FFmpeg composition execution creating a valid 9:16 vertical MP4.
   - FFprobe validation: verify video stream codec (h264), audio codec (aac), resolution (1080x1920), and positive duration.
4. **CapCut Compatibility Verification**:
   - `pycapcut` draft generation with distinct tracks (V1, V2, V3, A1, A2).
   - Validating generated `draft_content.json` schema against CapCut Desktop standards.
   - Verifying Windows metadata patcher writes compliant timestamps and paths.
5. **Publishing Adapters**:
   - Mocked and authenticated upload flow unit tests for YouTube, Facebook Page, and TikTok adapters.

---

## 2. Test Execution Matrix

| Test Suite | File Path | Tool | Scope |
| :--- | :--- | :--- | :--- |
| **Threads Crawler Test** | `tests/test_threads_crawler.py` | `pytest` | URL validation, HTML Relay extraction, comment tree nesting |
| **TTS Engine Test** | `tests/test_tts_engine.py` | `pytest` | Edge TTS synthesis, caching, Vietnamese text cleaning |
| **Card Render Test** | `tests/test_card_renderer.py` | `pytest` | Vietnamese typography, card sizing, line wrapping |
| **Video Composer Test** | `tests/test_video_composer.py` | `pytest` + `ffprobe` | FFmpeg filter graph, audio mixing, MP4 stream verification |
| **CapCut Exporter Test** | `tests/test_capcut_exporter.py` | `pytest` | Multi-track validation, metadata integrity, zip bundle |
| **Publishing Adapter Test** | `tests/test_publishing.py` | `pytest` | Resumable upload chunking, error handling, status persistence |
| **End-to-End Workflow Test**| `tests/test_e2e_workflow.py` | `pytest` | URL -> Crawl -> Select -> TTS -> Render -> CapCut Export |
