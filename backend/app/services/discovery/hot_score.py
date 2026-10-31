import math
from datetime import datetime, timezone
from typing import Optional, Tuple

class StudioHotScoreCalculator:
    """Calculates internal Studio Hot Score for discovered Threads posts,
    prioritizing active discussions and comment video potential."""

    HALF_LIFE_HOURS: float = 36.0

    @classmethod
    def calculate_score(
        cls,
        like_count: Optional[int],
        reply_count: Optional[int],
        repost_count: Optional[int],
        published_at_iso: Optional[str]
    ) -> Tuple[float, str]:
        likes = max(0, like_count) if like_count is not None else 0
        replies = max(0, reply_count) if reply_count is not None else 0
        reposts = max(0, repost_count) if repost_count is not None else 0

        # 1. Volume Score using log scale
        # Replies heavily prioritized (4.0x) as video studio is all about comments
        volume = (
            4.0 * math.log1p(replies)
            + 2.5 * math.log1p(reposts)
            + 1.0 * math.log1p(likes)
        )

        # 2. Recency Time Decay
        age_hours = 12.0  # default assumption if missing
        if published_at_iso:
            try:
                pub_dt = datetime.fromisoformat(published_at_iso.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                diff_sec = (now - pub_dt).total_seconds()
                age_hours = max(0.5, diff_sec / 3600.0)
            except Exception:
                pass

        time_decay = 0.5 ** (age_hours / cls.HALF_LIFE_HOURS)
        time_decay = max(0.08, min(1.0, time_decay))

        raw_score = volume * 7.2 * time_decay
        # Scale to 5.0 - 99.5
        score = round(max(5.0, min(99.5, raw_score)), 1)

        # 3. Generate human-readable ranking reason
        reason = cls._generate_reason(likes, replies, reposts, age_hours, score)
        return score, reason

    @classmethod
    def _generate_reason(
        cls,
        likes: int,
        replies: int,
        reposts: int,
        age_hours: float,
        score: float
    ) -> str:
        if replies >= 150:
            return f"🔥 Thảo luận bùng nổ: {replies:,} bình luận đang tranh luận sôi nổi"
        elif replies >= 40:
            return f"💬 Thảo luận sôi nổi: {replies} bình luận, lý tưởng để làm video"
        elif age_hours <= 12 and (likes + replies) >= 20:
            return f"⚡ Xu hướng mới nổi: Tương tác tăng nhanh trong {int(age_hours)}h qua"
        elif reposts >= 50:
            return f"🚀 Lan tỏa cao: {reposts:,} lượt chia sẻ trên Threads"
        elif likes >= 500:
            return f"⭐ Độ quan tâm cao: {likes:,} lượt thích"
        else:
            return "✨ Chủ đề gợi ý thảo luận phù hợp thị hiếu Việt Nam"

hot_score_calculator = StudioHotScoreCalculator()
