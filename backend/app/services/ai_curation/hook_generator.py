import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class HookOption(BaseModel):
    id: str
    style: str  # "curiosity", "conflict", "question", "custom"
    title_badge: str  # E.g. "Gây tò mò", "Kịch tính", "Câu hỏi tương tác"
    hook_text: str  # Display text on video hook card
    tts_text: str   # Cleaned text for TTS voiceover
    reason: str     # Why this hook retains viewers
    estimated_duration_sec: float = 3.0

    model_config = ConfigDict(from_attributes=True)

class HookGenerationResult(BaseModel):
    hooks: List[HookOption]
    post_summary: str
    detected_topic: str

class HookGenerator:
    """Generates viral, audience-retention opening hooks for Threads 9:16 videos."""

    def __init__(self):
        pass

    def _extract_core_topic(self, post_text: str) -> str:
        """Extracts the central theme or subject matter from the post."""
        clean = re.sub(r"https?://\S+", "", post_text).strip()
        first_sentence = re.split(r"[\n\.\?!]", clean)[0].strip()
        if len(first_sentence) > 70:
            first_sentence = first_sentence[:67] + "..."
        return first_sentence or "câu chuyện này"

    def generate_hooks(
        self,
        post_content: str,
        author_username: str = "",
        comments: Optional[List[Any]] = None
    ) -> HookGenerationResult:
        """Generates 3 tailored Vietnamese hooks for the given Threads post and comments."""
        topic_phrase = self._extract_core_topic(post_content)
        comments = comments or []

        # Analyze sentiment / tone
        post_lower = post_content.lower()
        is_humorous = any(w in post_lower for w in ["haha", "cười", "hài", "ảo", "vui", "bó tay", "lầy"])
        is_dramatic = any(w in post_lower for w in ["chia tay", "drama", "bóc phốt", "người yêu", "sốc", "khóc", "cảnh báo"])
        is_advice = any(w in post_lower for w in ["kinh nghiệm", "lời khuyên", "bài học", "hướng dẫn", "cách", "nên"])

        # Determine theme name
        theme = "Đời sống & Thảo luận"
        if is_humorous:
            theme = "Hài hước & Giải trí"
        elif is_dramatic:
            theme = "Drama & Tình huống kịch tính"
        elif is_advice:
            theme = "Kinh nghiệm & Góc nhìn cuộc sống"

        # 1. Hook 1: Curiosity / Mystery
        if is_humorous:
            hook1_text = f"Cứ tưởng chuyện đùa nhưng đọc bình luận mới thấy cười ra nước mắt!"
            hook1_tts = "Cứ tưởng chuyện đùa, nhưng đọc bình luận mới thấy cười ra nước mắt!"
            hook1_reason = "Tạo khoảng trống tò mò (Curiosity Gap) thôi thúc người xem chờ đón các pha đối đáp hài hước."
        elif is_dramatic:
            hook1_text = f"Bí mật khó tin đằng sau câu chuyện khiến cả cõi mạng Threads tranh cãi nảy lửa!"
            hook1_tts = "Bí mật khó tin đằng sau câu chuyện khiến cả cõi mạng đang tranh cãi nảy lửa!"
            hook1_reason = "Tạo cảm giác cấp bách và kịch tính, khơi dậy nhu cầu tìm hiểu sự thật."
        else:
            hook1_text = f"Điều gì khiến bài viết này thu hút hàng nghìn lượt bàn tán trên Threads?"
            hook1_tts = "Điều gì khiến bài viết này thu hút hàng nghìn lượt bàn tán xôn xao?"
            hook1_reason = "Tận dụng hiệu ứng đám đông (Social Proof) để giữ chân người xem ngay giây đầu."

        # 2. Hook 2: Conflict / Provocation
        if is_humorous:
            hook2_text = f"Tưởng không ai dám nói, hóa ra bình luận bên dưới còn đỉnh hơn cả bài gốc!"
            hook2_tts = "Tưởng không ai dám nói, ai ngờ các cao thủ bình luận bên dưới còn đỉnh hơn bài gốc!"
            hook2_reason = "Định vị bình luận là điểm nhấn đắt giá, giữ chân người xem tới punchline cuối."
        elif is_dramatic:
            hook2_text = f"90% mọi người đều phản đối cho đến khi nghe lời giải thích này..."
            hook2_tts = "Chín mươi phần trăm mọi người đều phản đối, cho đến khi nghe lời giải thích này..."
            hook2_reason = "Đánh vào mâu thuẫn quan điểm, khiến người xem tò mò phe nào sẽ chiến thắng."
        else:
            hook2_text = f"Một góc nhìn cực kỳ bất ngờ mà rất ít người nhận ra khi gặp chuyện này!"
            hook2_tts = "Một góc nhìn cực kỳ bất ngờ mà rất ít người nhận ra khi gặp tình huống này!"
            hook2_reason = "Kích thích khao khát học hỏi và tiếp nhận góc nhìn mới mẻ."

        # 3. Hook 3: Interactive Question
        if is_humorous:
            hook3_text = f"Nếu bạn rơi vào tình huống éo le này, bạn sẽ làm gì ngoài việc cười trừ?"
            hook3_tts = "Nếu bạn rơi vào tình huống dở khóc dở cười này, bạn sẽ làm gì ngoài việc cười trừ?"
            hook3_reason = "Đặt người xem vào tâm thế nhân vật chính để kích thích tương tác bình luận."
        elif is_dramatic:
            hook3_text = f"Đúng hay sai? Cùng nghe góc nhìn của cư dân mạng và cho ý kiến nhé!"
            hook3_tts = "Đúng hay là sai? Cùng nghe các ý kiến bên dưới và để lại quan điểm của bạn nhé!"
            hook3_reason = "Kêu gọi hành động (Call-to-Action) ngầm, kích thích tỷ lệ bình luận của video."
        else:
            hook3_text = f"Bạn đã từng gặp trường hợp tương tự thế này trong đời chưa?"
            hook3_tts = "Đã bao giờ bạn gặp phải trường hợp tương tự thế này trong đời chưa?"
            hook3_reason = "Khơi gợi trải nghiệm cá nhân tương đồng của người xem."

        def est_sec(text: str) -> float:
            words = len(text.split())
            return max(2.5, round(words / 3.0, 1))

        hooks = [
            HookOption(
                id="hook_curiosity",
                style="curiosity",
                title_badge="🔍 Gây tò mò & Bí ẩn",
                hook_text=hook1_text,
                tts_text=hook1_tts,
                reason=hook1_reason,
                estimated_duration_sec=est_sec(hook1_tts)
            ),
            HookOption(
                id="hook_conflict",
                style="conflict",
                title_badge="⚡ Kịch tính & Mâu thuẫn",
                hook_text=hook2_text,
                tts_text=hook2_tts,
                reason=hook2_reason,
                estimated_duration_sec=est_sec(hook2_tts)
            ),
            HookOption(
                id="hook_question",
                style="question",
                title_badge="💬 Câu hỏi tương tác",
                hook_text=hook3_text,
                tts_text=hook3_tts,
                reason=hook3_reason,
                estimated_duration_sec=est_sec(hook3_tts)
            ),
        ]

        return HookGenerationResult(
            hooks=hooks,
            post_summary=topic_phrase,
            detected_topic=theme
        )

hook_generator = HookGenerator()
