import math
from datetime import datetime, timezone
from typing import Optional, Tuple

YOUTH_VIRAL_BUZZWORDS = [
    "drama", "bóc phốt", "phốt", "tiểu phẩm", "vô tri", "red flag", "green flag",
    "trap", "toxic", "sếp", "đồng nghiệp", "deadline", "hóng", "flex",
    "overthinking", "crush", "ex", "tâm sự", "người yêu cũ", "cắm sừng",
    "say hi", "concert", "unpopular opinion", "trọ", "lương", "đi làm",
    "hẹn hò", "chia tay", "bạn thân", "thao túng", "ghosting", "peer pressure"
]

class StudioHotScoreCalculator:
    """Calculates internal Studio Hot Score based on genuine engagement metrics:
    - Comment Volume (highest weight: comment video studio needs rich dialogues)
    - Discussion Density (ratio of replies to likes, indicating active debates)
    - Exponential Recency Decay (breaking & today's posts heavily boosted)
    - Content Substance (optimal text length for voiceover and cards)
    """

    HALF_LIFE_HOURS: float = 24.0

    @classmethod
    def calculate_score(
        cls,
        like_count: Optional[int],
        reply_count: Optional[int],
        repost_count: Optional[int],
        published_at_iso: Optional[str],
        content: Optional[str] = None
    ) -> Tuple[float, str]:
        likes = max(0, like_count) if like_count is not None else 0
        replies = max(0, reply_count) if reply_count is not None else 0
        reposts = max(0, repost_count) if repost_count is not None else 0

        # 1. Base Engagement Volume (Log2 scale)
        # Replies heavily prioritized (5.0x) as comments drive video content
        vol_replies = 5.0 * math.log2(1.0 + replies)
        vol_reposts = 2.5 * math.log2(1.0 + reposts)
        vol_likes = 1.0 * math.log2(1.0 + likes)
        base_volume = vol_replies + vol_reposts + vol_likes

        # 2. Discussion Density / Controversy Index
        # High replies relative to likes indicates passionate discussion/debate
        density_multiplier = 1.0
        if likes > 0:
            density = replies / likes
            if density >= 0.25:
                density_multiplier = 1.25  # High debate density
            elif density >= 0.10:
                density_multiplier = 1.12
            elif density < 0.01 and likes > 500:
                density_multiplier = 0.85  # Passive lurker likes, few comments
        elif replies >= 20:
            density_multiplier = 1.20

        # 3. Recency Time Decay & Freshness Boost
        age_hours = 6.0
        if published_at_iso:
            try:
                pub_dt = datetime.fromisoformat(published_at_iso.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                diff_sec = (now - pub_dt).total_seconds()
                age_hours = max(0.1, diff_sec / 3600.0)
            except Exception:
                pass

        if age_hours <= 2.0:
            recency_mult = 1.65  # Breaking news right now
        elif age_hours <= 6.0:
            recency_mult = 1.45  # Trending today
        elif age_hours <= 12.0:
            recency_mult = 1.30  # Fresh today
        elif age_hours <= 24.0:
            recency_mult = 1.15  # In last 24h
        elif age_hours <= 48.0:
            recency_mult = 1.00
        else:
            # Exponential decay after 48h
            decay = 0.5 ** ((age_hours - 48.0) / cls.HALF_LIFE_HOURS)
            recency_mult = max(0.12, min(1.0, decay))

        # 4. Content Substance & Youth Buzzword Factor
        substance_mult = 1.0
        content_text = (content or "").strip()
        if len(content_text) < 15:
            substance_mult = 0.85  # Too brief
        elif 40 <= len(content_text) <= 500:
            substance_mult = 1.08  # Ideal length for card display & TTS

        c_low = content_text.lower()
        has_buzzword = any(bw in c_low for bw in YOUTH_VIRAL_BUZZWORDS)
        buzz_mult = 1.12 if has_buzzword else 1.0

        # Calculate Final Score
        raw = base_volume * 4.2 * density_multiplier * recency_mult * substance_mult * buzz_mult
        score = round(max(5.0, min(99.5, raw)), 1)

        # 5. Generate Evidence-Based Transparent Ranking Reason
        reason = cls._generate_reason(
            likes=likes,
            replies=replies,
            reposts=reposts,
            age_hours=age_hours,
            density_mult=density_multiplier,
            score=score
        )

        return score, reason

    @classmethod
    def _generate_reason(
        cls,
        likes: int,
        replies: int,
        reposts: int,
        age_hours: float,
        density_mult: float,
        score: float
    ) -> str:
        age_str = f"{int(age_hours)}h trước" if age_hours >= 1.0 else f"{max(1, int(age_hours * 60))}p trước"
        if age_hours >= 24.0:
            age_str = f"{int(age_hours / 24)} ngày trước"

        if density_mult >= 1.20 and replies >= 30:
            ratio_pct = int((replies / max(1, likes)) * 100) if likes > 0 else 100
            return f"🔥 Bão tranh luận: {replies:,} bình luận / {likes:,} thích ({ratio_pct}% tranh cãi) • Đăng {age_str}"
        elif age_hours <= 6.0 and replies >= 20:
            return f"⚡ Bùng nổ hôm nay: {replies} bình luận tăng nhanh • Vừa đăng {age_str}"
        elif replies >= 150:
            return f"💬 Kho bình luận phong phú: {replies:,} phản hồi • Đăng {age_str} • Rất hợp làm video"
        elif replies >= 40:
            return f"💬 Thảo luận sôi nổi: {replies} bình luận chia sẻ • {likes:,} thích • Đăng {age_str}"
        elif reposts >= 50:
            return f"🚀 Lan tỏa cao: {reposts:,} lượt chia sẻ • {likes:,} thích • Đăng {age_str}"
        elif likes >= 500:
            return f"⭐ Độ quan tâm cao: {likes:,} lượt thả tim • Đăng {age_str}"
        else:
            return f"✨ Chủ đề thịnh hành giới trẻ • Đăng {age_str}"

hot_score_calculator = StudioHotScoreCalculator()
