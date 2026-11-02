import math
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from backend.app.services.sfx.sfx_manager import sfx_manager
from backend.app.services.caption.caption_engine import caption_engine, CaptionSegment

logger = logging.getLogger("studio.timeline_planner")

class TimelineScene(BaseModel):
    id: str
    scene_index: int
    scene_type: str  # "hook", "post", "comment"
    author_username: str = ""
    author_display_name: str = ""
    display_text: str
    tts_text: str
    
    # Timing
    start_time_sec: float = 0.0
    duration_sec: float = 3.0
    end_time_sec: float = 3.0
    speech_duration_sec: float = 0.0
    pause_buffer_sec: float = 0.35
    
    # Media paths
    card_image_path: Optional[str] = None
    audio_path: Optional[str] = None
    
    # Dynamic Enhancements
    sfx_id: Optional[str] = None
    sfx_offset_sec: float = 0.0
    sfx_volume: float = 0.60
    zoom_effect: bool = False
    zoom_factor: float = 1.05
    transition_style: str = "fade"  # "fade", "slide", "none"
    is_punchline: bool = False
    
    model_config = ConfigDict(from_attributes=True)

class TimelinePlan(BaseModel):
    scenes: List[TimelineScene]
    total_duration_sec: float
    caption_segments: List[CaptionSegment]
    sfx_cues: List[Dict[str, Any]]
    has_hook: bool = False
    video_pace: str = "balanced"  # "fast", "balanced", "cinematic"

class TimelinePlanner:
    """Calculates optimal scene pacing, pauses, zoom effects, and audio sync for video production."""

    MIN_SCENE_DURATION = 2.2  # Minimum readable duration
    DEFAULT_PAUSE_BUFFER = 0.35  # Natural pause between speakers
    PUNCHLINE_PAUSE_BUFFER = 0.65  # Extra pause for humor to register

    def plan_timeline(
        self,
        hook: Optional[Dict[str, Any]],
        post: Any,
        comments: List[Any],
        pace: str = "balanced"  # "fast", "balanced", "cinematic"
    ) -> TimelinePlan:
        """Assembles a cohesive timeline with rhythm optimization and SFX placements."""
        scenes: List[TimelineScene] = []
        current_time = 0.0
        scene_idx = 0

        pace_multiplier = 0.85 if pace == "fast" else (1.15 if pace == "cinematic" else 1.0)

        # 1. Hook Scene (if enabled)
        if hook and hook.get("hook_text"):
            hook_text = hook.get("hook_text", "")
            hook_tts = hook.get("tts_text") or hook_text
            hook_speech_dur = float(hook.get("audio_duration_sec") or hook.get("estimated_duration_sec") or 3.0)
            hook_dur = max(self.MIN_SCENE_DURATION, hook_speech_dur + (self.DEFAULT_PAUSE_BUFFER * pace_multiplier))
            
            scenes.append(TimelineScene(
                id="scene_00_hook",
                scene_index=scene_idx,
                scene_type="hook",
                author_username="Threads Studio",
                author_display_name="Điểm Nhấn Mở Đầu",
                display_text=hook_text,
                tts_text=hook_tts,
                start_time_sec=round(current_time, 2),
                duration_sec=round(hook_dur, 2),
                end_time_sec=round(current_time + hook_dur, 2),
                speech_duration_sec=round(hook_speech_dur, 2),
                pause_buffer_sec=self.DEFAULT_PAUSE_BUFFER,
                sfx_id="whoosh",
                sfx_offset_sec=0.0,
                sfx_volume=0.55,
                zoom_effect=True,
                zoom_factor=1.06,
                transition_style="fade",
                is_punchline=False
            ))
            current_time += hook_dur
            scene_idx += 1

        # 2. Root Post Scene
        if post:
            post_content = getattr(post, "content", "") or ""
            post_author = getattr(post, "author_username", "threads_user") or "threads_user"
            post_display_name = getattr(post, "author_display_name", "") or post_author
            post_speech_dur = float(getattr(post, "audio_duration_sec", 0.0) or (len(post_content.split()) / 2.8))
            post_dur = max(self.MIN_SCENE_DURATION + 0.5, post_speech_dur + (self.DEFAULT_PAUSE_BUFFER * pace_multiplier))

            scenes.append(TimelineScene(
                id=f"scene_{scene_idx:02d}_post",
                scene_index=scene_idx,
                scene_type="post",
                author_username=post_author,
                author_display_name=post_display_name,
                display_text=post_content,
                tts_text=getattr(post, "tts_text", post_content) or post_content,
                start_time_sec=round(current_time, 2),
                duration_sec=round(post_dur, 2),
                end_time_sec=round(current_time + post_dur, 2),
                speech_duration_sec=round(post_speech_dur, 2),
                pause_buffer_sec=self.DEFAULT_PAUSE_BUFFER,
                sfx_id="pop",
                sfx_offset_sec=0.05,
                sfx_volume=0.60,
                zoom_effect=True,
                zoom_factor=1.04,
                transition_style="fade",
                is_punchline=False
            ))
            current_time += post_dur
            scene_idx += 1

        # 3. Comment Scenes
        total_comments = len(comments)
        for i, comment in enumerate(comments):
            display_text = getattr(comment, "display_text", "") or getattr(comment, "content", "") or ""
            tts_text = getattr(comment, "tts_text", "") or display_text
            author = getattr(comment, "author_username", "user") or "user"
            disp_author = getattr(comment, "author_display_name", "") or author
            
            # Speech duration from TTS or estimated word count
            c_audio_dur = float(getattr(comment, "audio_duration_sec", 0.0) or (len(tts_text.split()) / 3.0))
            is_last = (i == total_comments - 1)
            is_punchline = getattr(comment, "is_punchline", False) or is_last or ("haha" in display_text.lower())
            
            # Pause buffer: punchline or final comment gets longer pause
            pause = (self.PUNCHLINE_PAUSE_BUFFER if is_punchline else self.DEFAULT_PAUSE_BUFFER) * pace_multiplier
            c_dur = max(self.MIN_SCENE_DURATION, c_audio_dur + pause)

            # Assign SFX
            sfx_id = getattr(comment, "suggested_sfx", None)
            if not sfx_id:
                sfx_id = sfx_manager.suggest_sfx_for_scene(
                    scene_type="comment",
                    text=display_text,
                    is_punchline=is_punchline,
                    is_dialog_reply=bool(getattr(comment, "parent_comment_id", None))
                )

            scenes.append(TimelineScene(
                id=f"scene_{scene_idx:02d}_c_{i}",
                scene_index=scene_idx,
                scene_type="comment",
                author_username=author,
                author_display_name=disp_author,
                display_text=display_text,
                tts_text=tts_text,
                start_time_sec=round(current_time, 2),
                duration_sec=round(c_dur, 2),
                end_time_sec=round(current_time + c_dur, 2),
                speech_duration_sec=round(c_audio_dur, 2),
                pause_buffer_sec=round(pause, 2),
                sfx_id=sfx_id,
                sfx_offset_sec=0.04,
                sfx_volume=0.65 if is_punchline else 0.50,
                zoom_effect=is_punchline or (i % 2 == 1),
                zoom_factor=1.05 if is_punchline else 1.03,
                transition_style="fade",
                is_punchline=is_punchline
            ))
            current_time += c_dur
            scene_idx += 1

        # 4. Generate Captions & SFX Cues
        caption_segments: List[CaptionSegment] = []
        sfx_cues: List[Dict[str, Any]] = []

        for s in scenes:
            # Build caption segment
            line1, line2 = caption_engine.wrap_caption_lines(s.tts_text)
            keywords = caption_engine.extract_keywords(s.tts_text)
            caption_segments.append(CaptionSegment(
                id=f"cap_{s.id}",
                scene_index=s.scene_index,
                start_time_sec=s.start_time_sec,
                end_time_sec=s.end_time_sec,
                text=s.tts_text,
                highlighted_words=keywords,
                line1=line1,
                line2=line2
            ))

            # Build SFX cue
            if s.sfx_id and s.sfx_id != "none":
                sfx_cues.append({
                    "scene_index": s.scene_index,
                    "sfx_id": s.sfx_id,
                    "timestamp_sec": round(s.start_time_sec + s.sfx_offset_sec, 2),
                    "volume": s.sfx_volume,
                    "file_path": str(sfx_manager.get_sfx_path(s.sfx_id) or "")
                })

        return TimelinePlan(
            scenes=scenes,
            total_duration_sec=round(current_time, 2),
            caption_segments=caption_segments,
            sfx_cues=sfx_cues,
            has_hook=bool(hook and hook.get("hook_text")),
            video_pace=pace
        )

timeline_planner = TimelinePlanner()
