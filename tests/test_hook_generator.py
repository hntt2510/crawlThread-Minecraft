import pytest
from backend.app.services.ai_curation.hook_generator import hook_generator

def test_hook_generator_produces_three_diverse_styles():
    post_text = "Lần đầu tiên đi phỏng vấn xin việc mà gặp tình huống dở khóc dở cười này mọi người ạ."
    res = hook_generator.generate_hooks(post_content=post_text, author_username="nguyenvana")
    
    assert len(res.hooks) == 3
    styles = [h.style for h in res.hooks]
    assert "curiosity" in styles
    assert "conflict" in styles
    assert "question" in styles

    for h in res.hooks:
        assert len(h.hook_text) > 10
        assert len(h.tts_text) > 10
        assert h.estimated_duration_sec >= 2.5
        assert len(h.reason) > 5

def test_hook_generator_detects_humor_theme():
    post_text = "Không thể nhịn được cười với pha xử lý cồng kềnh của ông anh haha, ảo thật sự!"
    res = hook_generator.generate_hooks(post_content=post_text)
    assert "Hài hước" in res.detected_topic
