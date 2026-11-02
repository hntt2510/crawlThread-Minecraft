import subprocess
import shutil
import re
import math
import logging
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
from pydantic import BaseModel, Field

logger = logging.getLogger("studio.video_composer")

def get_ffmpeg_binary() -> str:
    """Finds available FFmpeg binary: System PATH or imageio_ffmpeg bundled binary."""
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and Path(exe).exists():
            return exe
    except Exception:
        pass
    return "ffmpeg"

class SFXCue(BaseModel):
    sfx_id: str
    file_path: Path
    timestamp_sec: float
    volume: float = 0.60

class VideoScene(BaseModel):
    card_image_path: Path
    audio_path: Optional[Path] = None
    duration_sec: float
    start_time_sec: float = 0.0
    sfx_cues: List[SFXCue] = []
    zoom_effect: bool = False
    is_hook: bool = False
    caption_text: Optional[str] = None

class VideoRenderConfig(BaseModel):
    output_path: Path
    scenes: List[VideoScene]
    background_video_path: Optional[Path] = None
    background_start_sec: float = 0.0
    background_volume: float = 0.20
    voice_volume: float = 1.0
    ducking_enabled: bool = True
    background_music_path: Optional[Path] = None
    ass_subtitle_path: Optional[Path] = None
    width: int = 1080
    height: int = 1920
    fps: int = 30

class FFmpegComposer:
    """Assembles 9:16 vertical short-form videos with background gameplay, cards, sound effects, and styled captions."""

    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_binary()

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
            progress_callback(10, "Đang hòa trộn giọng thuyết minh, nhạc nền và hiệu ứng âm thanh...")

        # 1. Build master audio track with voiceover, BGM ducking, and SFX
        master_audio = self._build_master_audio(config, total_duration, temp_dir)

        if progress_callback:
            progress_callback(30, "Đang ghép nối khung hình video 9:16, thẻ bình luận và phụ đề...")

        # 2. Build video stream with background, cards, and burned-in captions
        self._compose_video_with_audio(config, total_duration, master_audio, temp_dir, progress_callback)

        if progress_callback:
            progress_callback(100, "Dựng video hoàn tất!")

        return config.output_path

    def _build_master_audio(self, config: VideoRenderConfig, total_duration: float, temp_dir: Path) -> Path:
        """Concatenate voice clips, overlay SFX cues, and mix with ducked background music."""
        master_audio_path = temp_dir / "master_audio.wav"

        inputs = []
        filter_parts = []
        concat_inputs = []

        audio_input_count = 0

        # Step 1: Voiceover clips per scene
        for i, scene in enumerate(config.scenes):
            if scene.audio_path and scene.audio_path.exists():
                inputs.extend(["-i", str(scene.audio_path)])
                filter_parts.append(
                    f"[{audio_input_count}:a]apad=pad_dur={scene.duration_sec:.3f},atrim=0:{scene.duration_sec:.3f}[a{i}];"
                )
                concat_inputs.append(f"[a{i}]")
                audio_input_count += 1
            else:
                filter_parts.append(f"anullsrc=r=44100:cl=stereo,atrim=0:{scene.duration_sec:.3f}[a{i}];")
                concat_inputs.append(f"[a{i}]")

        # Concat all speech scenes
        concat_filter = f"{''.join(concat_inputs)}concat=n={len(config.scenes)}:v=0:a=1[speech_raw];"
        speech_filter = f"[speech_raw]volume={config.voice_volume:.2f}[speech];"

        # Step 2: Overlay SFX cues
        all_sfx_cues: List[SFXCue] = []
        for scene in config.scenes:
            all_sfx_cues.extend(scene.sfx_cues)

        speech_track_tag = "speech"
        
        if all_sfx_cues:
            valid_sfx = [cue for cue in all_sfx_cues if cue.file_path.exists()]
            if valid_sfx:
                curr_speech = "speech"
                for sfx_idx, cue in enumerate(valid_sfx):
                    inputs.extend(["-i", str(cue.file_path)])
                    sfx_input_tag = f"{audio_input_count}:a"
                    audio_input_count += 1
                    
                    delay_ms = int(max(0.0, cue.timestamp_sec) * 1000)
                    delayed_tag = f"sfx_del_{sfx_idx}"
                    filter_parts.append(
                        f"[{sfx_input_tag}]volume={cue.volume:.2f},adelay={delay_ms}|{delay_ms}[{delayed_tag}];"
                    )
                    
                    next_speech = f"speech_sfx_{sfx_idx}"
                    filter_parts.append(
                        f"[{curr_speech}][{delayed_tag}]amix=inputs=2:duration=first:dropout_transition=0[{next_speech}];"
                    )
                    curr_speech = next_speech
                speech_track_tag = curr_speech

        # Step 3: Background Music Ducking
        if config.background_music_path and config.background_music_path.exists() and config.background_volume > 0:
            inputs.extend(["-stream_loop", "-1", "-i", str(config.background_music_path)])
            bgm_idx = audio_input_count

            # Ducking: sidechain compress BGM when speech is active
            if config.ducking_enabled:
                filter_parts.append(
                    f"[{bgm_idx}:a]volume={config.background_volume:.2f}[bgm_norm];"
                    f"[{bgm_norm}][{speech_track_tag}]sidechaincompress="
                    f"threshold=0.08:ratio=6:attack=20:release=350[bgm_ducked];"
                    f"[{speech_track_tag}][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2[aout]"
                )
            else:
                filter_parts.append(
                    f"[{bgm_idx}:a]volume={config.background_volume:.2f}[bgm_norm];"
                    f"[{speech_track_tag}][bgm_norm]amix=inputs=2:duration=first[aout]"
                )
            final_audio_filter = ""
        else:
            final_audio_filter = f"[{speech_track_tag}]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[aout]"

        full_filter = "".join(filter_parts) + concat_filter + speech_filter + final_audio_filter

        cmd = [
            self.ffmpeg_bin, "-y",
            *inputs,
            "-filter_complex", full_filter,
            "-map", "[aout]",
            "-c:a", "pcm_s16le",
            "-t", f"{total_duration:.3f}",
            str(master_audio_path)
        ]

        logger.info(f"Building master audio: {' '.join(cmd[:12])}...")
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
        inputs = []
        filter_chains = []

        # 1. Background Video Input (Minecraft gameplay)
        if config.background_video_path and config.background_video_path.exists():
            inputs.extend([
                "-ss", f"{config.background_start_sec:.3f}",
                "-i", str(config.background_video_path)
            ])
            # Scale & crop to 1080x1920 (9:16 vertical)
            filter_chains.append(
                f"[0:v]scale={config.width}:{config.height}:force_original_aspect_ratio=increase,"
                f"crop={config.width}:{config.height}[bg_scaled];"
            )
            current_bg = "bg_scaled"
        else:
            # Fallback procedural gradient if no background video is provided
            filter_chains.append(
                f"color=c=0x111318:s={config.width}x{config.height}:d={total_duration:.3f}:r={config.fps}[bg_color];"
            )
            current_bg = "bg_color"

        # 2. Overlays for cards (Post card, comment cards, and hook card)
        timeline_curr = 0.0
        card_start_idx = inputs.count("-i")

        for i, scene in enumerate(config.scenes):
            img_input_idx = card_start_idx + i
            inputs.extend(["-i", str(scene.card_image_path)])

            t_start = timeline_curr
            t_end = timeline_curr + scene.duration_sec
            timeline_curr = t_end

            next_bg = f"v{i}"
            
            card_src = f"{img_input_idx}:v"
            if scene.zoom_effect:
                filter_chains.append(
                    f"[{card_src}]scale='min(iw*1.05,iw)':'min(ih*1.05,ih)':eval=frame[card_z{i}];"
                )
                card_src = f"card_z{i}"

            filter_chains.append(
                f"[{current_bg}][{card_src}]overlay="
                f"x=(W-w)/2:y=(H-h)/2-40:enable='between(t,{t_start:.3f},{t_end:.3f})'[{next_bg}];"
            )
            current_bg = next_bg

        # 3. Optional burned-in ASS Subtitles
        if config.ass_subtitle_path and config.ass_subtitle_path.exists():
            sub_path_escaped = str(config.ass_subtitle_path).replace("\\", "/").replace(":", "\\:")
            next_bg = "v_sub"
            filter_chains.append(
                f"[{current_bg}]subtitles='{sub_path_escaped}'[{next_bg}];"
            )
            current_bg = next_bg

        # 4. Audio Input
        audio_input_idx = inputs.count("-i")
        inputs.extend(["-i", str(master_audio)])

        full_video_filter = "".join(filter_chains)
        if full_video_filter.endswith(";"):
            full_video_filter = full_video_filter[:-1]

        cmd = [
            self.ffmpeg_bin, "-y",
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
