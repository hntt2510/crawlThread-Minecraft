# Architectural Decision Log (ADR)

## ADR-001: Direct Relay Stream Cache Parsing for Threads Crawler
- **Context**: Meta official API is primarily publishing-oriented and requires app review and business verification to read public threads. Using heavy headless browsers (Playwright) for every simple post request is slow (5-15s), memory-intensive, and prone to flakiness.
- **Decision**: Implement a primary provider using direct HTTP sessions with CSRF cookie initialization that extracts server-side rendered JSON from `<script data-sjs>` tags (`ScheduledServerJS` and `RelayPrefetchedStreamCache`).
- **Consequence**: Blazing fast retrieval (<1 second), zero external costs, zero API keys required for public posts, and reliable comment tree extraction. Fallback to GraphQL pagination and Playwright when needed.

---

## ADR-002: Multi-Provider TTS Architecture with Zero-Cost Edge-TTS Default
- **Context**: Vietnamese TTS options like FPT.AI or Google Cloud require paid API keys and credit cards, which would break out-of-the-box local usage if credentials are not yet configured.
- **Decision**: Adopt a pluggable `TTSProvider` pattern with Microsoft Edge TTS as the default out-of-the-box provider (`vi-VN-HoaiMyNeural` and `vi-VN-NamMinhNeural`), while maintaining full adapter support for FPT.AI and Google Cloud.
- **Consequence**: Immediate functionality on first run without friction or credit cards, with seamless upgrade path to FPT.AI regional accents.

---

## ADR-003: Multi-Track CapCut Desktop Generation via `pycapcut` and Metadata Patcher
- **Context**: Requirement specifies that the CapCut project must NOT be flattened into a single video track, but must preserve independent tracks for background, post card, comment cards, voiceovers, and music.
- **Decision**: Use `pycapcut` v0.0.4 with discrete `TrackType.video`, `TrackType.audio`, and `TrackType.text` assignments. Apply Windows metadata patching (`patch_capcut_metadata`) with UUID synchronization and relative project bundling.
- **Consequence**: The generated project can be opened directly in CapCut Desktop on Windows or packaged into a portable zip bundle for another user.

---

## ADR-004: FFmpeg Image-Based Card Rendering with Vietnamese Unicode Fonts
- **Context**: Rendering complex HTML/CSS or webviews into video can be slow and brittle. FFmpeg's `drawtext` filter often encounters font glyph missing issues on Windows when rendering Vietnamese tonal marks.
- **Decision**: Pre-render comment cards and post cards to crisp transparent PNGs using Python Pillow with proper text-wrapping and a certified Vietnamese Unicode font (Inter / Roboto / Segoe UI), then overlay them on the background video using FFmpeg filter chains.
- **Consequence**: 100% correct Vietnamese accents, crisp typography, predictable safe margins, and faster rendering speeds.
