import abc
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class VoiceMetadata(BaseModel):
    id: str
    name: str
    provider: str
    gender: str          # female, male
    accent: str          # Northern (Bắc), Southern (Nam), Central (Trung), General
    description: str = ""

class SynthesisResult(BaseModel):
    file_path: Path
    duration_ms: int
    file_size_bytes: int
    content_hash: str
    provider: str
    voice: str

def compute_tts_hash(provider: str, voice: str, rate: float, volume: float, text: str) -> str:
    payload = f"{provider}:{voice}:{rate:.2f}:{volume:.2f}:{text.strip()}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

class BaseTTSProvider(abc.ABC):
    @abc.abstractmethod
    def list_voices(self) -> List[VoiceMetadata]:
        pass

    @abc.abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: str,
        output_path: Path,
        rate: float = 1.0,
        volume: float = 1.0
    ) -> SynthesisResult:
        pass
