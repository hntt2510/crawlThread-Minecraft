import pytest
from backend.app.services.quality_checker.quality_checker import quality_checker
from backend.app.services.timeline.timeline_planner import TimelinePlan, TimelineScene

def test_quality_checker_flags_empty_scenes():
    plan = TimelinePlan(
        scenes=[],
        total_duration_sec=0.0,
        caption_segments=[],
        sfx_cues=[]
    )
    report = quality_checker.check_project_readiness(plan)
    assert report.is_passed is False
    assert any(e.code == "NO_SCENES" for e in report.errors)

def test_quality_checker_flags_excessive_duration():
    scenes = [
        TimelineScene(
            id=f"s_{i}",
            scene_index=i,
            scene_type="comment",
            display_text="Bình luận số " + str(i),
            tts_text="Bình luận số " + str(i),
            duration_sec=20.0
        )
        for i in range(6)
    ]
    plan = TimelinePlan(
        scenes=scenes,
        total_duration_sec=120.0,
        caption_segments=[],
        sfx_cues=[]
    )
    report = quality_checker.check_project_readiness(plan)
    assert any(w.code == "DURATION_TOO_LONG" for w in report.warnings)

def test_quality_checker_passes_healthy_plan():
    scenes = [
        TimelineScene(
            id="s_1",
            scene_index=0,
            scene_type="post",
            display_text="Bài viết chất lượng.",
            tts_text="Bài viết chất lượng.",
            duration_sec=5.0
        ),
        TimelineScene(
            id="s_2",
            scene_index=1,
            scene_type="comment",
            display_text="Bình luận sâu sắc.",
            tts_text="Bình luận sâu sắc.",
            duration_sec=4.0
        )
    ]
    plan = TimelinePlan(
        scenes=scenes,
        total_duration_sec=9.0,
        caption_segments=[],
        sfx_cues=[]
    )
    report = quality_checker.check_project_readiness(plan, voice_volume=1.0, bgm_volume=0.2)
    assert report.is_passed is True
    assert report.score >= 80
