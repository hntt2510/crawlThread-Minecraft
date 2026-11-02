import math
import wave
import struct
import logging
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel

from backend.app.core.config import settings

logger = logging.getLogger("studio.sfx_manager")

class SFXItem(BaseModel):
    id: str
    name: str
    category: str  # "transition", "punchline", "pop", "suspense", "ding"
    description: str
    file_path: str
    duration_ms: int
    default_volume: float = 0.65

class SFXManager:
    """Manages sound effect library, contextual auto-tagging, and fallback audio synthesis."""

    SFX_DEFINITIONS = [
        {"id": "whoosh", "name": "Chuyển cảnh vút nhanh (Whoosh)", "category": "transition", "desc": "Âm thanh lướt nhanh khi đổi phân cảnh hoặc chuyển slide.", "vol": 0.55},
        {"id": "pop", "name": "Bật nảy vui nhộn (Bubble Pop)", "category": "pop", "desc": "Âm thanh pop nhẹ khi thẻ bình luận xuất hiện.", "vol": 0.60},
        {"id": "punchline", "name": "Điểm nhấn hài hước (Punchline Hit)", "category": "punchline", "desc": "Âm thanh nhấn mạnh câu chốt bất ngờ, hài hước.", "vol": 0.70},
        {"id": "suspense", "name": "Hồi hộp kịch tính (Dramatic Hit)", "category": "suspense", "desc": "Âm thanh nhấn kịch tính khi tranh cãi hoặc tình tiết sốc.", "vol": 0.65},
        {"id": "ding", "name": "Chuông tinh khôi (Bright Chime)", "category": "ding", "desc": "Âm thanh chuông nhỏ cho bình luận nhiều like hoặc tích cực.", "vol": 0.50},
        {"id": "chime", "name": "Hài lòng ấm áp (Warm Bell)", "category": "ding", "desc": "Âm thanh chuông dịu cho cảm xúc ấm áp, đồng cảm.", "vol": 0.50},
    ]

    def __init__(self):
        self.sfx_dir = settings.DATA_DIR / "media" / "sfx"
        self.sfx_dir.mkdir(parents=True, exist_ok=True)
        self.ensure_default_sfx()

    def _generate_wav(self, output_path: Path, sound_type: str):
        """Synthesizes high-quality sound effects using pure Python standard library wave/math."""
        sample_rate = 44100
        n_channels = 2
        sampwidth = 2
        output_path.parent.mkdir(parents=True, exist_ok=True)

        frames = bytearray()

        if sound_type == "whoosh":
            # Filtered noise sweep from low to high frequency (0.35s)
            duration = 0.35
            total_samples = int(sample_rate * duration)
            for i in range(total_samples):
                t = i / sample_rate
                env = math.sin(math.pi * (t / duration)) ** 1.5
                freq = 200 + (1200 * (t / duration))
                sample = math.sin(2 * math.pi * freq * t) * env * 0.7
                int_sample = int(sample * 32767)
                frames.extend(struct.pack("<hh", int_sample, int_sample))

        elif sound_type == "pop":
            # Quick resonant pitch-drop bubble pop (0.12s)
            duration = 0.12
            total_samples = int(sample_rate * duration)
            for i in range(total_samples):
                t = i / sample_rate
                env = math.exp(-t * 35.0)
                freq = 800 - (500 * (t / duration))
                sample = math.sin(2 * math.pi * freq * t) * env * 0.8
                int_sample = int(sample * 32767)
                frames.extend(struct.pack("<hh", int_sample, int_sample))

        elif sound_type == "punchline":
            # Comedic brass staccato / double hit (0.4s)
            duration = 0.40
            total_samples = int(sample_rate * duration)
            for i in range(total_samples):
                t = i / sample_rate
                env = math.exp(-t * 8.0) * (0.8 + 0.2 * math.sin(2 * math.pi * 10 * t))
                f1 = 330.0  # E4
                f2 = 660.0  # E5
                sample = (0.6 * math.sin(2 * math.pi * f1 * t) + 0.4 * math.sin(2 * math.pi * f2 * t)) * env
                int_sample = int(sample * 32767)
                frames.extend(struct.pack("<hh", int_sample, int_sample))

        elif sound_type == "suspense":
            # Low dramatic brass boom with sub bass decay (0.6s)
            duration = 0.60
            total_samples = int(sample_rate * duration)
            for i in range(total_samples):
                t = i / sample_rate
                env = math.exp(-t * 5.0)
                f_sub = 90 - (30 * (t / duration))
                f_mid = 180 - (50 * (t / duration))
                sample = (0.7 * math.sin(2 * math.pi * f_sub * t) + 0.3 * math.sin(2 * math.pi * f_mid * t)) * env
                int_sample = int(sample * 32767)
                frames.extend(struct.pack("<hh", int_sample, int_sample))

        elif sound_type in ["ding", "chime"]:
            # Crisp metallic chime chord (C6 + E6 + G6) with long harmonic decay (0.5s)
            duration = 0.50
            total_samples = int(sample_rate * duration)
            for i in range(total_samples):
                t = i / sample_rate
                env = math.exp(-t * 6.5)
                f1 = 1046.50  # C6
                f2 = 1318.51  # E6
                f3 = 1567.98  # G6
                sample = (0.4 * math.sin(2 * math.pi * f1 * t) + 0.35 * math.sin(2 * math.pi * f2 * t) + 0.25 * math.sin(2 * math.pi * f3 * t)) * env
                int_sample = int(sample * 32767)
                frames.extend(struct.pack("<hh", int_sample, int_sample))

        else:
            duration = 0.2
            total_samples = int(sample_rate * duration)
            for i in range(total_samples):
                frames.extend(struct.pack("<hh", 0, 0))

        with wave.open(str(output_path), "wb") as wf:
            wf.setnchannels(n_channels)
            wf.setsampwidth(sampwidth)
            wf.setframerate(sample_rate)
            wf.writeframes(frames)

    def ensure_default_sfx(self):
        """Generates or verifies all default royalty-free sound effects."""
        for item in self.SFX_DEFINITIONS:
            sfx_id = item["id"]
            wav_path = self.sfx_dir / f"{sfx_id}.wav"
            if not wav_path.exists() or wav_path.stat().st_size < 100:
                try:
                    self._generate_wav(wav_path, sfx_id)
                except Exception as e:
                    logger.warning(f"Could not generate SFX {sfx_id}: {e}")

    def get_available_sfx(self) -> List[SFXItem]:
        """Returns list of all available sound effects."""
        self.ensure_default_sfx()
        results = []
        for d in self.SFX_DEFINITIONS:
            wav_path = self.sfx_dir / f"{d['id']}.wav"
            dur_ms = 350
            if wav_path.exists():
                try:
                    with wave.open(str(wav_path), "rb") as wf:
                        dur_ms = int((wf.getnframes() / wf.getframerate()) * 1000)
                except Exception:
                    pass

            results.append(SFXItem(
                id=d["id"],
                name=d["name"],
                category=d["category"],
                description=d["desc"],
                file_path=str(wav_path),
                duration_ms=dur_ms,
                default_volume=d["vol"]
            ))
        return results

    def get_sfx_path(self, sfx_id: str) -> Optional[Path]:
        """Resolves file path for an SFX by ID."""
        if not sfx_id or sfx_id == "none":
            return None
        p = self.sfx_dir / f"{sfx_id}.wav"
        if not p.exists():
            self._generate_wav(p, sfx_id)
        return p if p.exists() else None

    def suggest_sfx_for_scene(
        self,
        scene_type: str,
        text: str = "",
        is_punchline: bool = False,
        is_dialog_reply: bool = False
    ) -> Optional[str]:
        """Auto-recommends an appropriate sound effect based on scene context."""
        if scene_type == "hook":
            return "whoosh"
        if scene_type == "post":
            return "pop"
        if is_dialog_reply:
            return "whoosh"
        if is_punchline:
            return "punchline"

        lower = text.lower()
        if any(w in lower for w in ["haha", "cười", "vl", "hài", "bất ngờ", "quay xe", "lầy"]):
            return "punchline"
        if any(w in lower for w in ["nhưng", "thực ra", "sai", "sốc", "drama", "cảnh báo"]):
            return "suspense"
        if any(w in lower for w in ["thương", "ấm áp", "cảm động", "tuyệt vời", "yêu"]):
            return "chime"

        return "pop"

sfx_manager = SFXManager()
