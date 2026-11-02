import os
import random
import subprocess
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from backend.app.core.config import settings

logger = logging.getLogger("studio.gameplay_manager")

class GameplayMetadata(BaseModel):
    id: str
    filename: str
    file_path: str
    duration_sec: float
    width: int
    height: int
    is_vertical: bool
    category: str = "minecraft_parkour"  # "minecraft_parkour", "speedrun", "survival", "procedural"

class GameplayManager:
    """Manages gameplay footage library, auto-generation of fallback gameplay, and smart segment selection."""

    def __init__(self):
        self.gameplay_dir = settings.DATA_DIR / "media" / "gameplay"
        self.gameplay_dir.mkdir(parents=True, exist_ok=True)
        self.ensure_default_gameplay()

    def _get_video_duration(self, file_path: Path) -> float:
        """Probes video duration via ffprobe or ffmpeg."""
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path)
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(res.stdout.strip())
        except Exception:
            return 60.0

    def generate_procedural_gameplay(self, output_path: Path, duration_sec: int = 60) -> Path:
        """Generates a stylish 1080x1920 30fps procedural gameplay background when no local clips exist."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Generating procedural 9:16 background: {output_path}")

        # FFmpeg filter: dynamic moving gradients with particle grid pattern mimicking Minecraft block aesthetic
        filter_complex = (
            f"testsrc2=size=1080x1920:rate=30:duration={duration_sec},"
            f"hue=s=0.7:H='2*PI*t/30',"
            f"drawgrid=width=120:height=120:thickness=2:color=black@0.25,"
            f"boxblur=2:1"
        )
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", filter_complex,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            "-t", str(duration_sec),
            str(output_path)
        ]
        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except Exception as e:
            logger.error(f"Error generating procedural background: {e}")
        return output_path

    def ensure_default_gameplay(self):
        """Ensures at least one functional 9:16 gameplay video is available."""
        existing = list(self.gameplay_dir.glob("*.mp4"))
        if not existing:
            default_path = self.gameplay_dir / "sample_minecraft_gameplay.mp4"
            try:
                self.generate_procedural_gameplay(default_path, duration_sec=65)
            except Exception as e:
                logger.warning(f"Could not build initial procedural gameplay: {e}")

    def list_gameplay_clips(self) -> List[GameplayMetadata]:
        """Returns all registered gameplay clips with metadata."""
        self.ensure_default_gameplay()
        results = []
        for f in self.gameplay_dir.glob("*.mp4"):
            dur = self._get_video_duration(f)
            results.append(GameplayMetadata(
                id=f.stem,
                filename=f.name,
                file_path=str(f),
                duration_sec=dur,
                width=1080,
                height=1920,
                is_vertical=True,
                category="procedural" if "sample_" in f.name else "minecraft_parkour"
            ))
        return results

    def select_smart_segment(
        self,
        required_duration_sec: float,
        preferred_clip_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Selects a clip and a non-repeating start offset to fit required duration."""
        clips = self.list_gameplay_clips()
        if not clips:
            self.ensure_default_gameplay()
            clips = self.list_gameplay_clips()

        selected_clip = None
        if preferred_clip_id:
            selected_clip = next((c for c in clips if c.id == preferred_clip_id or c.filename == preferred_clip_id), None)

        if not selected_clip:
            selected_clip = random.choice(clips) if clips else None

        if not selected_clip:
            raise RuntimeError("Không tìm thấy video gameplay nào trong thư viện.")

        # Determine non-zero random start time to keep footage fresh
        max_start = max(0.0, selected_clip.duration_sec - required_duration_sec - 2.0)
        start_sec = round(random.uniform(0.0, max_start), 1) if max_start > 5.0 else 0.0

        return {
            "clip_id": selected_clip.id,
            "file_path": Path(selected_clip.file_path),
            "start_time_sec": start_sec,
            "duration_sec": selected_clip.duration_sec,
            "category": selected_clip.category
        }

gameplay_manager = GameplayManager()
