import pytest
import asyncio
from pathlib import Path
from backend.app.services.tts.tts_service import tts_service
from backend.app.services.tts.base import compute_tts_hash

@pytest.mark.asyncio
async def test_tts_voices_list():
    voices = tts_service.get_all_voices()
    assert len(voices) >= 2
    voice_ids = [v.id for v in voices]
    assert "vi-VN-HoaiMyNeural" in voice_ids
    assert "vi-VN-NamMinhNeural" in voice_ids

@pytest.mark.asyncio
async def test_tts_synthesis_and_caching(tmp_path):
    text = "Thử nghiệm giọng đọc tiếng Việt trên hệ thống Threads Studio."
    res1 = await tts_service.synthesize_text(
        text=text,
        provider="edge_tts",
        voice="vi-VN-HoaiMyNeural",
        rate=1.0
    )
    assert res1.file_path.exists()
    assert res1.duration_ms > 500
    assert res1.file_size_bytes > 500

    # Second call must hit cache immediately with matching content hash
    res2 = await tts_service.synthesize_text(
        text=text,
        provider="edge_tts",
        voice="vi-VN-HoaiMyNeural",
        rate=1.0
    )
    assert res1.content_hash == res2.content_hash
    assert res1.file_path == res2.file_path
