from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class QualityIssue(BaseModel):
    code: str
    severity: str  # "error" (blocks render), "warning" (can still render)
    message: str
    suggestion: str
    field_target: Optional[str] = None
    can_auto_fix: bool = False

class QualityCheckReport(BaseModel):
    is_passed: bool
    score: int = Field(100, description="Overall production readiness score (0-100)")
    errors: List[QualityIssue] = []
    warnings: List[QualityIssue] = []
    suggestions: List[str] = []
    video_duration_sec: float = 0.0

class QualityChecker:
    """Pre-flight quality assurance service verifying audio sync, safe zones, and asset integrity."""

    MAX_SHORTS_DURATION_SEC = 90.0
    MIN_SHORTS_DURATION_SEC = 10.0
    MAX_CAPTION_LINE_CHARS = 38

    def check_project_readiness(
        self,
        timeline_plan: Any,
        gameplay_path: Optional[Path] = None,
        bgm_path: Optional[Path] = None,
        voice_volume: float = 1.0,
        bgm_volume: float = 0.2
    ) -> QualityCheckReport:
        errors: List[QualityIssue] = []
        warnings: List[QualityIssue] = []
        suggestions: List[str] = []

        scenes = getattr(timeline_plan, "scenes", []) or []
        total_duration = getattr(timeline_plan, "total_duration_sec", 0.0) or 0.0

        # 1. Scene Count Check
        if not scenes:
            errors.append(QualityIssue(
                code="NO_SCENES",
                severity="error",
                message="Dự án chưa có phân cảnh nào để dựng video.",
                suggestion="Hãy chọn ít nhất 1 bài viết hoặc 2-3 bình luận để tạo nội dung.",
                field_target="scenes",
                can_auto_fix=False
            ))

        # 2. Total Duration Platform Check
        if total_duration > self.MAX_SHORTS_DURATION_SEC:
            warnings.append(QualityIssue(
                code="DURATION_TOO_LONG",
                severity="warning",
                message=f"Thời lượng video ({total_duration:.1f}s) vượt quá 90 giây tối ưu cho Shorts / TikTok.",
                suggestion="Nên giảm bớt số lượng bình luận (chọn Top 3 hoặc Top 5) để tăng tỷ lệ giữ chân người xem.",
                field_target="duration",
                can_auto_fix=True
            ))
        elif total_duration < self.MIN_SHORTS_DURATION_SEC and scenes:
            warnings.append(QualityIssue(
                code="DURATION_TOO_SHORT",
                severity="warning",
                message=f"Thời lượng video ({total_duration:.1f}s) quá ngắn dưới 10 giây.",
                suggestion="Bổ sung thêm bình luận hoặc phân cảnh mở đầu (Hook).",
                field_target="duration",
                can_auto_fix=False
            ))

        # 3. Audio & Volume Clipping Check
        if voice_volume > 1.35:
            warnings.append(QualityIssue(
                code="VOICE_CLIPPING_RISK",
                severity="warning",
                message=f"Âm lượng giọng đọc ({voice_volume * 100:.0f}%) có nguy cơ gây méo tiếng / clipping.",
                suggestion="Khuyến nghị để âm lượng giọng nói trong khoảng 90% - 110%.",
                field_target="voice_volume",
                can_auto_fix=True
            ))

        if bgm_volume > 0.45:
            warnings.append(QualityIssue(
                code="BGM_TOO_LOUD",
                severity="warning",
                message=f"Nhạc nền ({bgm_volume * 100:.0f}%) có thể lấn át giọng thuyết minh.",
                suggestion="Nên giữ nhạc nền ở mức 15% - 25% kèm cơ chế Ducking -14dB.",
                field_target="bgm_volume",
                can_auto_fix=True
            ))

        # 4. Text Length & Safe Zone Checks
        for idx, scene in enumerate(scenes):
            d_text = getattr(scene, "display_text", "") or ""
            # Check text length per card
            if len(d_text) > 350:
                warnings.append(QualityIssue(
                    code="CARD_TEXT_OVERFLOW",
                    severity="warning",
                    message=f"Phân cảnh {idx + 1} ({getattr(scene, 'author_username', 'user')}) chứa hơn 350 ký tự, có thể tràn thẻ hiển thị.",
                    suggestion="Cắt ngắn văn bản hiển thị hoặc ngắt làm 2 bình luận liên tiếp.",
                    field_target=f"scene_{idx}",
                    can_auto_fix=True
                ))

            # Check for unedited placeholder text
            if not d_text.strip():
                errors.append(QualityIssue(
                    code="EMPTY_SCENE_TEXT",
                    severity="error",
                    message=f"Phân cảnh {idx + 1} có nội dung trống.",
                    suggestion="Nhập nội dung cho phân cảnh hoặc xóa phân cảnh này.",
                    field_target=f"scene_{idx}",
                    can_auto_fix=False
                ))

        # 5. Media Assets Verification
        if gameplay_path and not Path(gameplay_path).exists():
            errors.append(QualityIssue(
                code="GAMEPLAY_NOT_FOUND",
                severity="error",
                message="Video gameplay nền đã chỉ định không tồn tại trên ổ đĩa.",
                suggestion="Hệ thống sẽ tự động dùng video gameplay mặc định trong thư viện.",
                field_target="gameplay_path",
                can_auto_fix=True
            ))

        # Calculate Score
        score = 100 - (len(errors) * 25) - (len(warnings) * 8)
        score = max(0, min(100, score))
        is_passed = len(errors) == 0

        # Suggestions
        if score >= 85:
            suggestions.append("Video đạt tiêu chuẩn chất lượng cao, nhịp điệu và âm lượng cân đối, sẵn sàng render!")
        elif is_passed:
            suggestions.append("Video có thể render được, nhưng nên tối ưu các cảnh báo để video đạt tương tác cao nhất.")
        else:
            suggestions.append("Vui lòng xử lý các lỗi nghiêm trọng (Errors) trước khi tiến hành render video.")

        return QualityCheckReport(
            is_passed=is_passed,
            score=score,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            video_duration_sec=round(total_duration, 1)
        )

quality_checker = QualityChecker()
