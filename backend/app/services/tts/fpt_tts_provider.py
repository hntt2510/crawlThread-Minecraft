import asyncio
import logging
from pathlib import Path
from typing import List
import httpx

from backend.app.services.tts.base import BaseTTSProvider, VoiceMetadata, SynthesisResult, compute_tts_hash
from backend.app.services.tts.edge_tts_provider import probe_audio_duration_ms

logger = logging.getLogger("studio.tts.fpt")

class FPTTTSProvider(BaseTTSProvider):
    """FPT.AI Speech Synthesis Provider supporting regional Vietnamese accents."""

    VOICES = [
        VoiceMetadata(id="banmai", name="Ban Mai (Nữ miền Bắc)", provider="fpt_ai", gender="female", accent="Miền Bắc"),
        VoiceMetadata(id="thuminh", name="Thu Minh (Nữ miền Bắc truyền cảm)", provider="fpt_ai", gender="female", accent="Miền Bắc"),
        VoiceMetadata(id="giahuy", name="Gia Huy (Nam miền Trung)", provider="fpt_ai", gender="male", accent="Miền Trung"),
        VoiceMetadata(id="myan", name="Mỹ An (Nữ miền Nam)", provider="fpt_ai", gender="female", accent="Miền Nam"),
        VoiceMetadata(id="minhquang", name="Minh Quang (Nam miền Nam)", provider="fpt_ai", gender="male", accent="Miền Nam"),
    ]

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

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
        if not self.api_key:
            raise ValueError("FPT.AI Speech API Key chưa được cấu hình. Vui lòng nhập API Key trong phần Cài đặt.")

        # Map speed: FPT uses -3 to 3 (0 is normal)
        speed = 0
        if rate > 1.0:
            speed = min(3, int((rate - 1.0) * 4))
        elif rate < 1.0:
            speed = max(-3, int((rate - 1.0) * 4))

        headers = {
            "api_key": self.api_key,
            "voice": voice,
            "speed": str(speed),
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post("https://api.fpt.ai/hmi/tts/v5", headers=headers, content=text.encode("utf-8"))
            if resp.status_code != 200:
                raise RuntimeError(f"FPT.AI API lỗi HTTP {resp.status_code}: {resp.text}")
            
            data = resp.json()
            async_url = data.get("async")
            if not async_url:
                raise RuntimeError(f"FPT.AI không trả về liên kết tải file âm thanh: {data}")

            # Poll until async audio file is ready
            audio_bytes = None
            for _ in range(30):
                await asyncio.sleep(1.0)
                poll_resp = await client.get(async_url)
                if poll_resp.status_code == 200:
                    audio_bytes = poll_resp.content
                    break
            
            if not audio_bytes:
                raise TimeoutError("Quá thời gian chờ tạo âm thanh từ FPT.AI.")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(audio_bytes)

        duration_ms = probe_audio_duration_ms(output_path)
        file_size = output_path.stat().st_size
        content_hash = compute_tts_hash("fpt_ai", voice, rate, volume, text)

        return SynthesisResult(
            file_path=output_path,
            duration_ms=duration_ms,
            file_size_bytes=file_size,
            content_hash=content_hash,
            provider="fpt_ai",
            voice=voice
        )
