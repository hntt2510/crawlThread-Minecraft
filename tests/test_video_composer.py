import subprocess
import pytest
from pathlib import Path
from backend.app.services.card_renderer.card_generator import card_generator
from backend.app.services.video_composer.ffmpeg_composer import ffmpeg_composer, VideoScene, VideoRenderConfig
from backend.app.services.tts.tts_service import tts_service

@pytest.mark.asyncio
async def test_video_composer_full_render(tmp_path):
    # 1. Generate 2 cards
    card1 = tmp_path / "card1.png"
    card2 = tmp_path / "card2.png"
    card_generator.create_card("zuck", "Mark Zuckerberg", "Bài viết gốc trên Threads", card1, "post")
    card_generator.create_card("fan", "Bình Luận Viên", "Bình luận tiếng Việt số 1", card2, "comment")

    # 2. Synthesize audio
    tts1 = await tts_service.synthesize_text("Bài viết gốc trên Threads", "edge_tts", "vi-VN-HoaiMyNeural")
    tts2 = await tts_service.synthesize_text("Bình luận tiếng Việt số một", "edge_tts", "vi-VN-NamMinhNeural")

    scenes = [
        VideoScene(card_image_path=card1, audio_path=tts1.file_path, duration_sec=max(2.0, tts1.duration_ms / 1000.0 + 0.5)),
        VideoScene(card_image_path=card2, audio_path=tts2.file_path, duration_sec=max(2.0, tts2.duration_ms / 1000.0 + 0.5)),
    ]

    out_mp4 = tmp_path / "final_output.mp4"
    config = VideoRenderConfig(
        output_path=out_mp4,
        scenes=scenes,
        width=1080,
        height=1920,
        fps=30
    )

    rendered_path = ffmpeg_composer.render_video(config)
    assert rendered_path.exists()
    assert rendered_path.stat().st_size > 10000

    # 3. FFprobe verification
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,codec_name",
        "-of", "csv=p=0",
        str(rendered_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
    parts = res.stdout.strip().split(",")
    # e.g. "h264,1080,1920"
    assert "h264" in parts or "1080" in parts
    assert any("1080" in p for p in parts)
    assert any("1920" in p for p in parts)
