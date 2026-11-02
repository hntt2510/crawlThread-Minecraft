import pytest
from backend.app.services.timeline.timeline_planner import timeline_planner

class MockPost:
    content = "Một trải nghiệm nhớ đời khi đi du lịch tự túc lần đầu ở Đà Lạt."
    author_username = "traveler_vn"
    author_display_name = "Thích Du Lịch"
    audio_duration_sec = 4.0

class MockComment:
    def __init__(self, id, display, tts, dur=3.0, is_punch=False):
        self.id = id
        self.display_text = display
        self.tts_text = tts
        self.author_username = "guest"
        self.author_display_name = "Khách"
        self.audio_duration_sec = dur
        self.is_punchline = is_punch

def test_timeline_planner_assembles_scenes_and_captions():
    hook = {
        "hook_text": "Bí mật chuyến đi Đà Lạt khiến ai cũng bất ngờ!",
        "tts_text": "Bí mật chuyến đi Đà Lạt khiến ai cũng phải bất ngờ!",
        "audio_duration_sec": 3.0
    }
    comments = [
        MockComment("c1", "Đi một mình buồn lắm bạn ơi.", "Đi một mình buồn lắm bạn ơi.", dur=2.5),
        MockComment("c2", "Nhưng gặp người yêu ở đó thì vui gấp đôi haha!", "Nhưng gặp người yêu ở đó thì vui gấp đôi luôn!", dur=3.2, is_punch=True)
    ]

    plan = timeline_planner.plan_timeline(
        hook=hook,
        post=MockPost(),
        comments=comments,
        pace="balanced"
    )

    assert plan.has_hook is True
    assert len(plan.scenes) == 4  # 1 Hook + 1 Post + 2 Comments
    assert plan.total_duration_sec > 10.0

    # Hook scene checks
    hook_scene = plan.scenes[0]
    assert hook_scene.scene_type == "hook"
    assert hook_scene.sfx_id == "whoosh"
    assert hook_scene.zoom_effect is True

    # Punchline scene checks
    last_scene = plan.scenes[3]
    assert last_scene.is_punchline is True
    assert last_scene.pause_buffer_sec >= 0.6  # extra punchline pause

    # Captions generated
    assert len(plan.caption_segments) == 4
    assert len(plan.sfx_cues) >= 2
