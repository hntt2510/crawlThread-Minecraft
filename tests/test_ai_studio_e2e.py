import pytest
from pathlib import Path
from backend.app.core.config import settings
from backend.app.services.ai_curation.comment_curator import comment_curator
from backend.app.services.ai_curation.hook_generator import hook_generator
from backend.app.services.timeline.timeline_planner import timeline_planner
from backend.app.services.caption.caption_engine import caption_engine
from backend.app.services.quality_checker.quality_checker import quality_checker
from backend.app.services.card_renderer.card_generator import card_generator
from backend.app.services.video_composer.ffmpeg_composer import ffmpeg_composer, VideoScene, VideoRenderConfig, SFXCue
from backend.app.services.capcut_exporter.builder import CapCutExporter
from backend.app.services.sfx.sfx_manager import sfx_manager
from backend.app.services.gameplay.gameplay_manager import gameplay_manager

class E2EPost:
    id = "p_e2e_01"
    content = "Lần đầu tiên đi cắm trại ở Ba Vì và những bài học cười ra nước mắt."
    author_username = "camtrai_vui"
    author_display_name = "Cắm Trại Vui Vẻ"
    like_count = 340
    reply_count = 42

class E2EComment:
    def __init__(self, id, content, likes=50, replies=5, parent_id=None):
        self.id = id
        self.content = content
        self.like_count = likes
        self.reply_count = replies
        self.parent_comment_id = parent_id
        self.author_username = f"user_{id}"
        self.author_display_name = f"Thành Viên {id}"

def test_full_ai_video_studio_pipeline(tmp_path):
    # 1. AI Comment Curation
    comments_pool = [
        E2EComment("c1", "Nhớ mang theo thuốc chống muỗi nha, muỗi to như con ruồi haha!", likes=120),
        E2EComment("c2", "Tưởng đi nghỉ dưỡng ai ngờ đi hành xác suốt 2 ngày trời.", likes=85),
        E2EComment("c3", "Pass đồ cắm trại giá rẻ ib zalo 0912345678", likes=1), # Spam
        E2EComment("c4", "Nhưng được cái ngắm hoàng hôn đỉnh chóp, đáng từng xu!", likes=95),
        E2EComment("c5", "Đúng nhận sai cãi: đi cắm trại về chỉ muốn ngủ bù 3 ngày haha!", likes=210),
    ]

    curation = comment_curator.curate(comments_pool, target_count=3, mode="balanced")
    assert len(curation.curated_comments) == 3
    assert curation.total_filtered_spam >= 1
    # Check that spam c3 was excluded
    chosen_ids = [c.comment_id for c in curation.curated_comments]
    assert "c3" not in chosen_ids

    # 2. AI Hook Generation
    hook_res = hook_generator.generate_hooks(post_content=E2EPost.content, author_username=E2EPost.author_username)
    assert len(hook_res.hooks) == 3
    selected_hook = hook_res.hooks[0]

    # 3. Timeline Planning
    plan = timeline_planner.plan_timeline(
        hook=selected_hook.model_dump(),
        post=E2EPost(),
        comments=curation.curated_comments,
        pace="fast"
    )
    assert plan.has_hook is True
    assert len(plan.scenes) == 5  # 1 Hook + 1 Post + 3 Comments
    assert plan.total_duration_sec > 10.0

    # 4. Smart Caption Generation (ASS file)
    ass_file = tmp_path / "test_captions.ass"
    caption_engine.generate_ass_subtitles(plan.caption_segments, ass_file)
    assert ass_file.exists()
    assert ass_file.stat().st_size > 200

    # 5. Pre-flight Quality Check
    qc_report = quality_checker.check_project_readiness(plan, voice_volume=1.0, bgm_volume=0.20)
    assert qc_report.is_passed is True
    assert qc_report.score >= 80

    # 6. Render Card Images & Construct Scenes
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)
    video_scenes = []

    for s in plan.scenes:
        card_p = cards_dir / f"{s.id}.png"
        card_generator.create_card(
            author_username=s.author_username,
            author_display_name=s.author_display_name,
            content=s.display_text,
            output_path=card_p,
            card_type="hook" if s.scene_type == "hook" else ("post" if s.scene_type == "post" else "comment")
        )
        assert card_p.exists()
        
        cues = []
        if s.sfx_id and sfx_manager.get_sfx_path(s.sfx_id):
            cues.append(SFXCue(
                sfx_id=s.sfx_id,
                file_path=sfx_manager.get_sfx_path(s.sfx_id),
                timestamp_sec=s.start_time_sec + s.sfx_offset_sec,
                volume=s.sfx_volume
            ))

        video_scenes.append(VideoScene(
            card_image_path=card_p,
            duration_sec=s.duration_sec,
            start_time_sec=s.start_time_sec,
            sfx_cues=cues,
            zoom_effect=s.zoom_effect,
            is_hook=(s.scene_type == "hook")
        ))

    # 7. Render Video with FFmpeg
    output_mp4 = tmp_path / "e2e_video.mp4"
    bg_segment = gameplay_manager.select_smart_segment(required_duration_sec=plan.total_duration_sec)

    render_cfg = VideoRenderConfig(
        output_path=output_mp4,
        scenes=video_scenes,
        background_video_path=bg_segment["file_path"],
        background_start_sec=bg_segment["start_time_sec"],
        background_volume=0.15,
        voice_volume=1.0,
        ass_subtitle_path=ass_file,
        width=1080,
        height=1920,
        fps=30
    )

    rendered_video = ffmpeg_composer.render_video(render_cfg)
    assert rendered_video.exists()
    assert rendered_video.stat().st_size > 10_000

    # 8. Export to CapCut Desktop Multi-Track Project
    capcut_exporter = CapCutExporter()
    export_dir = tmp_path / "capcut_out"
    export_res = capcut_exporter.export_project(
        project_name="AI_Studio_E2E_Test",
        scenes=video_scenes,
        background_video_path=bg_segment["file_path"],
        install_to_local=False,
        output_dir=export_dir
    )

    assert export_res.draft_dir.exists()
    assert (export_res.draft_dir / "draft_content.json").exists()
    assert (export_res.draft_dir / "draft_meta_info.json").exists()
    assert export_res.package_zip_path is not None
    assert export_res.package_zip_path.exists()
