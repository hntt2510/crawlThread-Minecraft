import logging
from pathlib import Path
from typing import List
import httpx

from backend.app.services.tts.base import BaseTTSProvider, VoiceMetadata, SynthesisResult, compute_tts_hash
from backend.app.services.tts.edge_tts_provider import probe_audio_duration_ms

logger = logging.getLogger("studio.tts.google")

class GoogleTTSProvider(BaseTTSProvider):
    """Google Cloud Text-to-Speech Provider."""

    VOICES = [
        VoiceMetadata(id="vi-VN-Wavenet-A", name="Google Wavenet A (Nữ)", provider="google_tts", gender="female", accent="Toàn quốc"),
        VoiceMetadata(id="vi-VN-Wavenet-B", name="Google Wavenet B (Nam)", provider="google_tts", gender="male", accent="Toàn quốc"),
        VoiceMetadata(id="vi-VN-Wavenet-C", name="Google Wavenet C (Nữ)", provider="google_tts", gender="female", accent="Toàn quốc"),
        VoiceMetadata(id="vi-VN-Wavenet-D", name="Google Wavenet D (Nam)", provider="google_tts", gender="male", accent="Toàn quốc"),
    ]

    def __init__(self, credentials_file: str = ""):
        self.credentials_file = credentials_file

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
        if not self.credentials_file or not Path(self.credentials_file).exists():
            raise ValueError("Google Cloud TTS credentials file chưa được cấu hình hoặc file không tồn tại.")

        # In production Google Cloud environments with service account json
        try:
            from google.cloud import texttospeech
            client = texttospeech.TextToSpeechClient()
            s_input = texttospeech.SynthesisInput(text=text)
            s_voice = texttospeech.VoiceSelectionParams(language_code="vi-VN", name=voice)
            s_audio = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=rate,
                volume_gain_db=(volume - 1.0) * 10
            )
            response = client.synthesize_speech(input=s_input, voice=s_voice, audio_config=s_audio)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(response.audio_content)
        except Exception as e:
            raise RuntimeError(f"Lỗi khởi tạo Google TTS client: {e}")

        duration_ms = probe_audio_duration_ms(output_path)
        file_size = output_path.stat().st_size
        content_hash = compute_tts_hash("google_tts", voice, rate, volume, text)

        return SynthesisResult(
            file_path=output_path,
            duration_ms=duration_ms,
            file_size_bytes=file_size,
            content_hash=content_hash,
            provider="google_tts",
            voice=voice
        )
