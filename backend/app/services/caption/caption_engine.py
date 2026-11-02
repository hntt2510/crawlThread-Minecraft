import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CaptionWord(BaseModel):
    word: str
    is_keyword: bool = False

class CaptionSegment(BaseModel):
    id: str
    scene_index: int
    start_time_sec: float
    end_time_sec: float
    text: str
    highlighted_words: List[str] = []
    line1: str = ""
    line2: str = ""

class CaptionConfig(BaseModel):
    enabled: bool = True
    font_name: str = "Segoe UI"
    font_size: int = 44
    primary_color: str = "&H00FFFFFF"  # BGR format for ASS (White)
    highlight_color: str = "&H0015CCFA"  # Gold / Yellow BGR
    outline_color: str = "&H00101012"  # Deep dark outline
    outline_width: int = 4
    shadow_depth: int = 2
    vertical_margin: int = 340  # Safe zone above TikTok/Reels caption bar (bottom 340px)
    max_chars_per_line: int = 32

class CaptionEngine:
    """Engine for generating synchronized, styled Vietnamese captions with keyword highlighting."""

    KEYWORD_REGEX = re.compile(
        r"\b(sốc|bất ngờ|không thể tin|cười|hài|đúng|sai|quan điểm|bí mật|lời khuyên|sự thật|kinh khủng|quá đỉnh|out trình|chết cười|bó tay)\b",
        re.IGNORECASE
    )

    def wrap_caption_lines(self, text: str, max_chars: int = 32) -> tuple[str, str]:
        """Splits long text into at most 2 balanced readable lines."""
        words = text.split()
        if not words:
            return "", ""

        total_len = len(text)
        if total_len <= max_chars:
            return text, ""

        # Find best split point near the middle
        mid_word_idx = len(words) // 2
        line1 = " ".join(words[:mid_word_idx])
        line2 = " ".join(words[mid_word_idx:])

        # If line1 is still too long, re-balance
        if len(line1) > max_chars and mid_word_idx > 1:
            line1 = " ".join(words[:mid_word_idx - 1])
            line2 = " ".join(words[mid_word_idx - 1:])

        return line1, line2

    def extract_keywords(self, text: str) -> List[str]:
        """Detects high-impact words to highlight."""
        matches = self.KEYWORD_REGEX.findall(text)
        return list(set(matches))

    def generate_ass_subtitles(
        self,
        segments: List[CaptionSegment],
        output_path: Path,
        config: Optional[CaptionConfig] = None
    ) -> Path:
        """Generates an ASS subtitle file formatted for 1080x1920 vertical video with safe zones."""
        cfg = config or CaptionConfig()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        def to_ass_time(sec: float) -> str:
            hrs = int(sec // 3600)
            mins = int((sec % 3600) // 60)
            secs = int(sec % 60)
            csecs = int(round((sec - int(sec)) * 100))
            return f"{hrs:01d}:{mins:02d}:{secs:02d}.{csecs:02d}"

        # Header for ASS 1080x1920
        ass_content = [
            "[Script Info]",
            "Title: Threads Comment Studio Captions",
            "ScriptType: v4.00+",
            "PlayResX: 1080",
            "PlayResY: 1920",
            "WrapStyle: 0",
            "ScaledBorderAndShadow: yes",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            (
                f"Style: StudioCaption,{cfg.font_name},{cfg.font_size},{cfg.primary_color},"
                f"&H000000FF,{cfg.outline_color},&H80000000,-1,0,0,0,100,100,0,0,1,"
                f"{cfg.outline_width},{cfg.shadow_depth},2,60,60,{cfg.vertical_margin},1"
            ),
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        ]

        for seg in segments:
            start_str = to_ass_time(seg.start_time_sec)
            end_str = to_ass_time(seg.end_time_sec)
            line1, line2 = self.wrap_caption_lines(seg.text, cfg.max_chars_per_line)

            # Highlight keywords inside text
            formatted_text = f"{line1}\\N{line2}" if line2 else line1
            for kw in seg.highlighted_words:
                kw_escaped = re.escape(kw)
                formatted_text = re.sub(
                    f"({kw_escaped})",
                    f"{{\\\\c{cfg.highlight_color}}}\\1{{\\\\c{cfg.primary_color}}}",
                    formatted_text,
                    flags=re.IGNORECASE
                )

            ass_content.append(
                f"Dialogue: 0,{start_str},{end_str},StudioCaption,,0,0,0,,{formatted_text}"
            )

        output_path.write_text("\n".join(ass_content), encoding="utf-8")
        return output_path

caption_engine = CaptionEngine()
