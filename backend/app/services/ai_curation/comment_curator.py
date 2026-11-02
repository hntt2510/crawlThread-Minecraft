import re
import math
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class CuratedComment(BaseModel):
    comment_id: str
    author_username: str
    author_display_name: str = ""
    display_text: str
    tts_text: str
    like_count: Optional[int] = 0
    reply_count: Optional[int] = 0
    parent_comment_id: Optional[str] = None
    nesting_depth: int = 0
    
    # AI Scoring details
    overall_score: float = Field(0.0, description="Overall viral potential score (0 - 100)")
    humor_score: float = 0.0
    emotion_score: float = 0.0
    controversy_score: float = 0.0
    story_score: float = 0.0
    engagement_score: float = 0.0
    is_thread_dialog: bool = False
    
    selection_reason: str = ""
    suggested_sfx: Optional[str] = None  # e.g. "punchline", "pop", "suspense", "whoosh"
    punchline_pause_sec: float = 0.0

    model_config = ConfigDict(from_attributes=True)

class CurationResult(BaseModel):
    curated_comments: List[CuratedComment]
    total_evaluated: int
    total_filtered_spam: int
    selection_mode: str
    summary_insight: str = ""

# Common Vietnamese chat contractions to normalize for natural voiceover reading
VIETNAMESE_SLANG_NORMALIZER: Dict[str, str] = {
    r"\bko\b": "không",
    r"\bk\b": "không",
    r"\bkh\b": "không",
    r"\bhem\b": "hổng",
    r"\bdc\b": "được",
    r"\bđc\b": "được",
    r"\bvs\b": "với",
    r"\bj\b": "gì",
    r"\bng\b": "người",
    r"\bmn\b": "mọi người",
    r"\bbt\b": "biết",
    r"\bnhiu\b": "nhiêu",
    r"\bbn\b": "bao nhiêu",
    r"\bb\b": "bạn",
    r"\bm\b": "mình",
    r"\bthui\b": "thôi",
    r"\bz\b": "vậy",
    r"\bv\b": "vậy",
    r"\bok\b": "ô kê",
    r"\boke\b": "ô kê",
    r"\bokela\b": "ô kê la",
    r"\bđr\b": "đúng rồi",
    r"\bdr\b": "đúng rồi",
    r"\bchx\b": "chưa",
    r"\bch\b": "chưa",
    r"\bnhg\b": "nhưng",
    r"\bbik\b": "biết",
    r"\btui\b": "tôi",
    r"\bnta\b": "người ta",
    r"\bntn\b": "như thế nào",
    r"\bns\b": "nói",
    r"\btks\b": "cảm ơn",
    r"\bcam on\b": "cảm ơn",
    r"\bvk\b": "vợ",
    r"\bck\b": "chồng",
    r"\bcrush\b": "người trong mộng",
    r"\bpro\b": "cao thủ",
    r"\bvl\b": "vãi",
    r"\bcl\b": "vãi cả",
    r"\bclgt\b": "cái gì thế",
    r"\bhaizz\b": "haizz",
    r"\bhaha+\b": "ha ha",
    r"\bhehe+\b": "he he",
    r"\bhihi+\b": "hi hi",
}

# Spam & Advertisement regex triggers
SPAM_PATTERNS = [
    re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE),
    re.compile(r"\b(inbox|ib|zalo|pass đồ|mua bán|giá rẻ|freeship|liên hệ)\b", re.IGNORECASE),
    re.compile(r"\b(tuyển sỉ|đại lý|cộng tác viên|ctv|việc làm online)\b", re.IGNORECASE),
    re.compile(r"\b(0\d{9,10})\b"),  # Phone numbers
    re.compile(r"(.)\1{5,}", re.IGNORECASE),  # Spam char flooding: e.g. "aaaaaaa"
]

# Vietnamese Humor indicators
HUMOR_KEYWORDS = [
    "haha", "hehe", "hihi", "cười", "hài", "mắc cười", "bật ngửa", "cạn lời",
    "ngã ngửa", "quỳ", "chết cười", "bái phục", "ảo thật", "đúng nhận sai cãi",
    "out trình", "bó tay", "má ơi", "trời ơi", "troll", "khóc thét", "bất ngờ",
    "vl", "cl", "lầy", "lầy lội", "cười ẻ", "cười bò", "hề hước", "hài hước",
    "bẻ lái", "quay xe", "đội quần", "quê xệ", "cứu tôi", "xin vĩnh biệt cụ"
]

# Vietnamese Storytelling indicators
STORY_KEYWORDS = [
    "hồi đó", "ngày xưa", "mình từng", "tôi từng", "kinh nghiệm", "kể nghe",
    "chuyện là", "hồi sinh viên", "lúc trước", "bản thân", "có lần", "hôm qua",
    "hồi nhỏ", "nhớ lại", "gia đình", "bạn thân", "thực tế", "vụ này", "bài học"
]

# Vietnamese Controversy / Debate indicators
CONTROVERSY_KEYWORDS = [
    "nhưng mà", "thực ra", "thật ra", "quan điểm", "chưa chắc", "sai rồi",
    "ngược lại", "thấy lạ", "tại sao", "vô lý", "tranh cãi", "không đồng ý",
    "bất công", "định kiến", "tiêu chuẩn kép", "thất vọng", "khó hiểu"
]

# Vietnamese Emotion / Empathy indicators
EMOTION_KEYWORDS = [
    "thương", "xúc động", "cảm động", "ngưỡng mộ", "tuyệt vời", "ấm áp",
    "chia buồn", "tội nghiệp", "đồng cảm", "thương tâm", "nước mắt", "nghẹn ngào",
    "tự hào", "biết ơn", "chân thành", "yêu thương", "chữa lành"
]

class CommentCurator:
    """Smart AI Comment Selection Service that evaluates humor, emotional resonance,
    storytelling, debate potential, and parent-child dialog continuity."""

    def clean_text_for_tts(self, text: str) -> str:
        """Cleans colloquial chat abbreviations and emojis for smooth, natural voiceover pronunciation."""
        if not text:
            return ""
        
        normalized = text
        # 1. Replace common acronyms / chat abbreviations
        for pattern, replacement in VIETNAMESE_SLANG_NORMALIZER.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
            
        # 2. Remove URLs
        normalized = re.sub(r"https?://\S+", "", normalized)
        
        # 3. Remove excessive punctuation flooding (e.g. "!!!!!" -> "!")
        normalized = re.sub(r"!{2,}", "!", normalized)
        normalized = re.sub(r"\?{2,}", "?", normalized)
        normalized = re.sub(r"\.{3,}", "...", normalized)
        
        # 4. Remove emoji glyphs or decorative symbols that cause TTS glitches
        # Keep Vietnamese letters, numbers, and standard punctuation (. , ! ? - " ' / :)
        clean_tts = re.sub(r"[^\w\s\.,!\?\-'\":áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ]", " ", normalized)
        clean_tts = re.sub(r"\s+", " ", clean_tts).strip()
        
        return clean_tts or text

    def is_spam_or_low_quality(self, text: str, like_count: Optional[int] = 0) -> bool:
        """Flags advertisements, spam, empty or non-value comments."""
        if not text:
            return True
            
        trimmed = text.strip()
        # Too short to carry any context
        if len(trimmed) < 4:
            return True
            
        # Repetitive single word or emoji only
        for pat in SPAM_PATTERNS:
            if pat.search(trimmed):
                # Allow high-like comments if it's just mild laughter or short reaction
                if (like_count or 0) < 15:
                    return True

        return False

    def evaluate_comment(
        self,
        comment: Any,
        parent_comment: Optional[Any] = None,
        max_likes_in_pool: int = 1
    ) -> CuratedComment:
        """Analyzes a single comment across multi-dimensional criteria."""
        content = getattr(comment, "content", "") or ""
        author = getattr(comment, "author_username", "user") or "user"
        display_name = getattr(comment, "author_display_name", "") or author
        c_id = str(getattr(comment, "id", ""))
        like_count = getattr(comment, "like_count", 0) or 0
        reply_count = getattr(comment, "reply_count", 0) or 0
        parent_id = getattr(comment, "parent_comment_id", None)
        nesting_depth = getattr(comment, "nesting_depth", 0) or 0

        lower_content = content.lower()
        word_count = len(content.split())

        # 1. Humor calculation
        humor_hits = sum(1 for kw in HUMOR_KEYWORDS if kw in lower_content)
        has_twist = bool(re.search(r"(\.\.\.|quay xe|ai dè|thì ra|bất ngờ)", lower_content))
        humor_score = min(100.0, (humor_hits * 22.0) + (20.0 if has_twist else 0.0))

        # 2. Storytelling calculation
        story_hits = sum(1 for kw in STORY_KEYWORDS if kw in lower_content)
        # Optimal story length is between 15 and 80 words
        length_factor = 30.0 if 15 <= word_count <= 80 else (10.0 if word_count > 80 else 5.0)
        story_score = min(100.0, (story_hits * 25.0) + length_factor)

        # 3. Controversy & Debate calculation
        debate_hits = sum(1 for kw in CONTROVERSY_KEYWORDS if kw in lower_content)
        has_question = "?" in content
        controversy_score = min(100.0, (debate_hits * 24.0) + (15.0 if has_question else 0.0))

        # 4. Emotion calculation
        emotion_hits = sum(1 for kw in EMOTION_KEYWORDS if kw in lower_content)
        emotion_score = min(100.0, emotion_hits * 30.0)

        # 5. Engagement normalized (0 - 100)
        norm_likes = min(100.0, (like_count / max(1, max_likes_in_pool)) * 100.0)
        norm_replies = min(100.0, (reply_count * 15.0))
        engagement_score = (norm_likes * 0.7) + (norm_replies * 0.3)

        # 6. Conversation thread bonus
        is_thread_dialog = False
        thread_bonus = 0.0
        if parent_comment and parent_id:
            is_thread_dialog = True
            thread_bonus = 18.0

        # Weighted Composite Score
        # Video viewers on TikTok/Shorts prefer Humor > Storytelling > Debate > Engagement
        overall_score = (
            (humor_score * 0.32) +
            (story_score * 0.25) +
            (controversy_score * 0.18) +
            (emotion_score * 0.10) +
            (engagement_score * 0.15) +
            thread_bonus
        )

        # Punish comments that are too short (less than 6 words) or too long (>120 words)
        if word_count < 6:
            overall_score *= 0.65
        elif word_count > 120:
            overall_score *= 0.80

        overall_score = round(min(100.0, max(0.0, overall_score)), 1)

        # Determine Primary Reason & Suggested SFX & Timing
        reasons = []
        suggested_sfx = None
        punchline_pause = 0.3

        if is_thread_dialog:
            reasons.append("Phản hồi đối đáp thông minh bẻ lái nội dung bài viết gốc")
            suggested_sfx = "whoosh"
            punchline_pause = 0.4
        elif humor_score >= 50.0:
            reasons.append("Bình luận hài hước cao trào có nhiều tương tác dí dỏm")
            suggested_sfx = "punchline"
            punchline_pause = 0.65
        elif story_score >= 50.0:
            reasons.append("Chia sẻ trải nghiệm chân thực, cuốn hút người nghe")
            suggested_sfx = "pop"
            punchline_pause = 0.4
        elif controversy_score >= 40.0:
            reasons.append("Góc nhìn tranh biện kích thích người xem để lại bình luận")
            suggested_sfx = "suspense"
            punchline_pause = 0.5
        elif emotion_score >= 40.0:
            reasons.append("Cảm xúc chân thành tạo sự đồng cảm sâu sắc với cộng đồng")
            suggested_sfx = "chime"
            punchline_pause = 0.4
        elif engagement_score >= 50.0:
            reasons.append(f"Top tương tác nổi bật ({like_count:,} lượt thích, {reply_count} phản hồi)")
            suggested_sfx = "ding"
            punchline_pause = 0.35
        else:
            reasons.append("Góc nhìn bổ trợ thú vị làm phong phú nội dung video")
            suggested_sfx = "pop"
            punchline_pause = 0.3

        selection_reason = ". ".join(reasons)
        tts_text = self.clean_text_for_tts(content)

        return CuratedComment(
            comment_id=c_id,
            author_username=author,
            author_display_name=display_name,
            display_text=content,
            tts_text=tts_text,
            like_count=like_count,
            reply_count=reply_count,
            parent_comment_id=parent_id,
            nesting_depth=nesting_depth,
            overall_score=overall_score,
            humor_score=round(humor_score, 1),
            emotion_score=round(emotion_score, 1),
            controversy_score=round(controversy_score, 1),
            story_score=round(story_score, 1),
            engagement_score=round(engagement_score, 1),
            is_thread_dialog=is_thread_dialog,
            selection_reason=selection_reason,
            suggested_sfx=suggested_sfx,
            punchline_pause_sec=punchline_pause,
        )

    def curate(
        self,
        comments: List[Any],
        target_count: int = 5,
        mode: str = "balanced"  # "balanced", "humor", "story", "controversy"
    ) -> CurationResult:
        """Filters spam, evaluates scores, and selects optimal comments for video storytelling."""
        if not comments:
            return CurationResult(
                curated_comments=[],
                total_evaluated=0,
                total_filtered_spam=0,
                selection_mode=mode,
                summary_insight="Chưa có bình luận nào để phân tích."
            )

        # 1. Filter out spam and low-value entries
        valid_candidates = []
        filtered_count = 0
        comments_by_id = {str(getattr(c, "id", "")): c for c in comments}

        max_likes = max((getattr(c, "like_count", 0) or 0) for c in comments) if comments else 1

        for c in comments:
            content = getattr(c, "content", "") or ""
            likes = getattr(c, "like_count", 0) or 0
            if self.is_spam_or_low_quality(content, likes):
                filtered_count += 1
                continue
            valid_candidates.append(c)

        if not valid_candidates:
            # If all were filtered, take the least spammy ones
            valid_candidates = comments[:target_count]

        # 2. Evaluate each valid comment
        evaluated: List[CuratedComment] = []
        for c in valid_candidates:
            parent_id = getattr(c, "parent_comment_id", None)
            parent = comments_by_id.get(str(parent_id)) if parent_id else None
            evaluated.append(self.evaluate_comment(c, parent_comment=parent, max_likes_in_pool=max_likes))

        # 3. Sort according to mode
        if mode == "humor":
            evaluated.sort(key=lambda x: (x.humor_score, x.overall_score), reverse=True)
        elif mode == "story":
            evaluated.sort(key=lambda x: (x.story_score, x.overall_score), reverse=True)
        elif mode == "controversy":
            evaluated.sort(key=lambda x: (x.controversy_score, x.overall_score), reverse=True)
        else:  # "balanced"
            evaluated.sort(key=lambda x: x.overall_score, reverse=True)

        # 4. Pick top N while respecting conversation threads (if parent selected, try to include witty reply)
        selected: List[CuratedComment] = []
        selected_ids = set()

        for candidate in evaluated:
            if len(selected) >= target_count:
                break
            if candidate.comment_id in selected_ids:
                continue

            selected.append(candidate)
            selected_ids.add(candidate.comment_id)

            # Check if there is an interesting reply to this parent comment in evaluated pool
            if len(selected) < target_count:
                reply = next((c for c in evaluated if c.parent_comment_id == candidate.comment_id and c.comment_id not in selected_ids), None)
                if reply and reply.overall_score >= 35.0:
                    selected.append(reply)
                    selected_ids.add(reply.comment_id)

        # Summary insight in Vietnamese
        avg_score = sum(c.overall_score for c in selected) / max(1, len(selected))
        summary = f"Đã tuyển chọn {len(selected)} bình luận tiêu biểu đạt điểm chất lượng trung bình {avg_score:.1f}/100 theo tiêu chí {mode}."

        return CurationResult(
            curated_comments=selected[:target_count],
            total_evaluated=len(comments),
            total_filtered_spam=filtered_count,
            selection_mode=mode,
            summary_insight=summary
        )

comment_curator = CommentCurator()
