import asyncio
import subprocess
import logging
from pathlib import Path
from typing import List
import edge_tts

from backend.app.services.tts.base import BaseTTSProvider, VoiceMetadata, SynthesisResult, compute_tts_hash

logger = logging.getLogger("studio.tts.edge")

def probe_audio_duration_ms(file_path: Path) -> int:
    """Accurately probe audio duration in milliseconds using ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path)
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        seconds = float(res.stdout.strip())
        return int(seconds * 1000)
    except Exception as e:
        logger.warning(f"ffprobe duration error on {file_path}: {e}")
        size = file_path.stat().st_size
        return max(500, int((size / 16000) * 1000))

class EdgeTTSProvider(BaseTTSProvider):
    VOICES = [
        VoiceMetadata(
            id="vi-VN-HoaiMyNeural",
            name="Hoài My (Nữ - Truyền cảm, Phổ biến)",
            provider="edge_tts",
            gender="female",
            accent="Bắc / Toàn quốc",
            description="Giọng nữ chuẩn tự nhiên, diễn cảm, rõ lời."
        ),
        VoiceMetadata(
            id="vi-VN-NamMinhNeural",
            name="Nam Minh (Nam - Trầm ấm, Rõ ràng)",
            provider="edge_tts",
            gender="male",
            accent="Bắc / Toàn quốc",
            description="Giọng nam trầm ấm, phát âm chuẩn, phù hợp bình luận."
        ),
    ]

    def list_voices(self) -> List[VoiceMetadata]:
        return self.VOICES

    async def synthesize(
        self,
        text: str,
        voice: str,
        output_path: Path,
        rate: float = 1.0,
        volume: float = 1.0
    ) -> SynthesisResult:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        valid_voice = voice if any(v.id == voice for v in self.VOICES) else "vi-VN-HoaiMyNeural"
        
        kwargs = {}
        if abs(rate - 1.0) > 0.01:
            rate_percent = int((rate - 1.0) * 100)
            kwargs["rate"] = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"
        if abs(volume - 1.0) > 0.01:
            vol_percent = int((volume - 1.0) * 100)
            kwargs["volume"] = f"+{vol_percent}%" if vol_percent >= 0 else f"{vol_percent}%"

        last_err = None
        for attempt in range(3):
            try:
                communicate = edge_tts.Communicate(text=text.strip(), voice=valid_voice, **kwargs)
                await communicate.save(str(output_path))
                break
            except Exception as e:
                last_err = e
                await asyncio.sleep(0.5)
        else:
            if last_err:
                raise last_err

        duration_ms = probe_audio_duration_ms(output_path)
        file_size = output_path.stat().st_size
        content_hash = compute_tts_hash("edge_tts", valid_voice, rate, volume, text)

        return SynthesisResult(
            file_path=output_path,
            duration_ms=duration_ms,
            file_size_bytes=file_size,
            content_hash=content_hash,
            provider="edge_tts",
            voice=valid_voice
        )
