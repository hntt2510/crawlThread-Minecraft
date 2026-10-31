import logging
from pathlib import Path
from typing import List, Dict, Optional

from backend.app.core.config import settings
from backend.app.services.tts.base import BaseTTSProvider, VoiceMetadata, SynthesisResult, compute_tts_hash
from backend.app.services.tts.edge_tts_provider import EdgeTTSProvider, probe_audio_duration_ms
from backend.app.services.tts.fpt_tts_provider import FPTTTSProvider
from backend.app.services.tts.google_tts_provider import GoogleTTSProvider

logger = logging.getLogger("studio.tts.service")

class TTSService:
    def __init__(self):
        self.providers: Dict[str, BaseTTSProvider] = {
            "edge_tts": EdgeTTSProvider(),
            "fpt_ai": FPTTTSProvider(api_key=settings.FPTAI_API_KEY),
            "google_tts": GoogleTTSProvider(credentials_file=settings.GOOGLE_APPLICATION_CREDENTIALS),
        }
        self.cache_dir = settings.CACHE_DIR / "audio"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_all_voices(self) -> List[VoiceMetadata]:
        all_voices = []
        for p in self.providers.values():
            all_voices.extend(p.list_voices())
        return all_voices

    def get_provider(self, provider_name: str) -> BaseTTSProvider:
        if provider_name not in self.providers:
            return self.providers["edge_tts"]
        return self.providers[provider_name]

    async def synthesize_text(
        self,
        text: str,
        provider: str = "edge_tts",
        voice: str = "vi-VN-HoaiMyNeural",
        rate: float = 1.0,
        volume: float = 1.0,
        output_file_name: Optional[str] = None
    ) -> SynthesisResult:
        """Synthesize text with deterministic caching."""
        clean_text = text.strip()
        if not clean_text:
            raise ValueError("Văn bản đọc không được để trống.")

        content_hash = compute_tts_hash(provider, voice, rate, volume, clean_text)
        cached_file = self.cache_dir / f"{content_hash}.mp3"

        if cached_file.exists() and cached_file.stat().st_size > 500:
            logger.info(f"Using cached audio for hash: {content_hash}")
            duration_ms = probe_audio_duration_ms(cached_file)
            return SynthesisResult(
                file_path=cached_file,
                duration_ms=duration_ms,
                file_size_bytes=cached_file.stat().st_size,
                content_hash=content_hash,
                provider=provider,
                voice=voice
            )

        target_provider = self.get_provider(provider)
        target_path = cached_file if not output_file_name else (self.cache_dir / output_file_name)

        result = await target_provider.synthesize(
            text=clean_text,
            voice=voice,
            output_path=target_path,
            rate=rate,
            volume=volume
        )
        return result

tts_service = TTSService()
