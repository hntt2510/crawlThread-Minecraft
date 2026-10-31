import subprocess
import re
import math
import logging
from pathlib import Path
from typing import List, Optional, Callable
from pydantic import BaseModel

logger = logging.getLogger("studio.video_composer")

class VideoScene(BaseModel):
    card_image_path: Path
    audio_path: Optional[Path] = None
    duration_sec: float
    start_time_sec: float = 0.0

class VideoRenderConfig(BaseModel):
    output_path: Path
    scenes: List[VideoScene]
    background_video_path: Optional[Path] = None
    background_start_sec: float = 0.0
    background_volume: float = 0.2
    voice_volume: float = 1.0
    background_music_path: Optional[Path] = None
    width: int = 1080
    height: int = 1920
    fps: int = 30

class FFmpegComposer:
    """Assembles 9:16 vertical short-form videos with background gameplay, cards, and synchronized voiceovers."""

    def render_video(self, config: VideoRenderConfig, progress_callback: Optional[Callable[[int, str], None]] = None) -> Path:
        if not config.scenes:
            raise ValueError("Không có phân cảnh nào để dựng video.")

        total_duration = sum(s.duration_sec for s in config.scenes)
        if total_duration <= 0.5:
            raise ValueError("Tổng thời lượng video quá ngắn.")

        config.output_path.parent.mkdir(parents=True, exist_ok=True)
        temp_dir = config.output_path.parent / "temp_render"
        temp_dir.mkdir(parents=True, exist_ok=True)

        if progress_callback:
            progress_callback(10, "Đang chuẩn bị luồng âm thanh...")

        # 1. Build master audio track
        master_audio = self._build_master_audio(config, total_duration, temp_dir)

        if progress_callback:
            progress_callback(30, "Đang ghép nối khung hình video và nhạc nền...")

        # 2. Build video stream with background and overlay cards
        self._compose_video_with_audio(config, total_duration, master_audio, temp_dir, progress_callback)

        if progress_callback:
            progress_callback(100, "Dựng video hoàn tất!")

        return config.output_path

    def _build_master_audio(self, config: VideoRenderConfig, total_duration: float, temp_dir: Path) -> Path:
        """Concatenate voice clips at exact scene timestamps and mix with background music."""
        master_audio_path = temp_dir / "master_audio.wav"

        # Generate silence or audio mix
        # Create an input list for ffmpeg
        inputs = []
        filter_parts = []
        concat_inputs = []

        curr_time = 0.0
        audio_idx = 0

        for i, scene in enumerate(config.scenes):
            if scene.audio_path and scene.audio_path.exists():
                inputs.extend(["-i", str(scene.audio_path)])
                # Pad audio to exact scene duration if shorter
                filter_parts.append(f"[{audio_idx}:a]apad=pad_dur={scene.duration_sec:.3f},atrim=0:{scene.duration_sec:.3f}[a{i}];")
                concat_inputs.append(f"[a{i}]")
                audio_idx += 1
            else:
                # Generate silence for this scene
                filter_parts.append(f"anullsrc=r=44100:cl=stereo,atrim=0:{scene.duration_sec:.3f}[a{i}];")
                concat_inputs.append(f"[a{i}]")

        # Concat all speech scenes
        concat_filter = f"{''.join(concat_inputs)}concat=n={len(config.scenes)}:v=0:a=1[speech_raw];"
        speech_filter = f"[speech_raw]volume={config.voice_volume:.2f}[speech];"

        # Final audio stream formatting or mixing
        if config.background_music_path and config.background_music_path.exists():
            bgm_idx = audio_idx
            inputs.extend(["-stream_loop", "-1", "-i", str(config.background_music_path)])
            bgm_vol = config.background_volume
            final_audio_filter = (
                f"[{bgm_idx}:a]atrim=0:{total_duration:.3f},volume={bgm_vol:.2f}[bgm];"
                f"[speech][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            )
        else:
            final_audio_filter = f"[speech]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[aout]"

        full_filter = "".join(filter_parts) + concat_filter + speech_filter + final_audio_filter

        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", full_filter,
            "-map", "[aout]",
            "-c:a", "pcm_s16le",
            "-t", f"{total_duration:.3f}",
            str(master_audio_path)
        ]

        logger.info(f"Building master audio: {' '.join(cmd)}")
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            logger.error(f"FFmpeg audio error: {res.stderr}")
            raise RuntimeError(f"Lỗi xử lý âm thanh: {res.stderr[-300:]}")

        return master_audio_path

    def _compose_video_with_audio(
        self,
        config: VideoRenderConfig,
        total_duration: float,
        master_audio: Path,
        temp_dir: Path,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ):
        """Overlay cards onto background video (or generated dark gradient) along with audio."""
        inputs = []
        filter_chains = []

        # 1. Background input
        if config.background_video_path and config.background_video_path.exists():
            # Loop background video
            inputs.extend([
                "-stream_loop", "-1",
                "-ss", f"{config.background_start_sec:.2f}",
                "-i", str(config.background_video_path)
            ])
            # Scale & crop to 1080x1920
            filter_chains.append(
                f"[0:v]scale={config.width}:{config.height}:force_original_aspect_ratio=increase,"
                f"crop={config.width}:{config.height},setsar=1[bg];"
            )
        else:
            # Generate animated clean gradient background if no video file provided
            filter_chains.append(
                f"color=c=#0f172a:s={config.width}x{config.height}:r={config.fps}:d={total_duration:.3f}[bg];"
            )

        # 2. Add each card as an image input
        card_start_idx = 1 if (config.background_video_path and config.background_video_path.exists()) else 0
        current_bg = "bg"
        timeline_curr = 0.0

        for i, scene in enumerate(config.scenes):
            img_input_idx = card_start_idx + i
            inputs.extend(["-i", str(scene.card_image_path)])

            t_start = timeline_curr
            t_end = timeline_curr + scene.duration_sec
            timeline_curr = t_end

            next_bg = f"v{i}"
            # Overlay card centered horizontally (x = (W - w)/2), centered vertically (y = (H - h)/2)
            # with smooth alpha enable window
            filter_chains.append(
                f"[{current_bg}][{img_input_idx}:v]overlay="
                f"x=(W-w)/2:y=(H-h)/2-50:enable='between(t,{t_start:.3f},{t_end:.3f})'[{next_bg}];"
            )
            current_bg = next_bg

        # 3. Audio input
        audio_input_idx = len(inputs) // 2  # next available input index
        inputs.extend(["-i", str(master_audio)])

        # Final video link
        full_video_filter = "".join(filter_chains)
        # Remove trailing semicolon
        if full_video_filter.endswith(";"):
            full_video_filter = full_video_filter[:-1]

        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", full_video_filter,
            "-map", f"[{current_bg}]",
            "-map", f"{audio_input_idx}:a",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-r", str(config.fps),
            "-t", f"{total_duration:.3f}",
            str(config.output_path)
        ]

        logger.info(f"Running video render: {' '.join(cmd[:15])}...")
        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True, encoding="utf-8", errors="replace")

        # Parse progress from stderr
        time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
        while True:
            line = process.stderr.readline()
            if not line and process.poll() is not None:
                break
            match = time_pattern.search(line)
            if match and progress_callback:
                hours = int(match.group(1))
                minutes = int(match.group(2))
                seconds = float(match.group(3))
                current_sec = hours * 3600 + minutes * 60 + seconds
                pct = min(98, 30 + int((current_sec / max(0.1, total_duration)) * 68))
                progress_callback(pct, f"Đang xuất video: {current_sec:.1f}s / {total_duration:.1f}s")

        if process.returncode != 0:
            err = process.stderr.read()
            raise RuntimeError(f"FFmpeg render thất bại (code {process.returncode}): {err[-400:]}")

ffmpeg_composer = FFmpegComposer()
