import pytest
from backend.app.services.ai_curation.comment_curator import comment_curator, CuratedComment

class MockComment:
    def __init__(self, id, content, likes=0, replies=0, parent_id=None, depth=0, author="user"):
        self.id = id
        self.content = content
        self.like_count = likes
        self.reply_count = replies
        self.parent_comment_id = parent_id
        self.nesting_depth = depth
        self.author_username = author
        self.author_display_name = author.title()

def test_comment_curator_cleans_vietnamese_slang():
    raw_text = "tui ko bt bạn nói j luôn á, nhưng mà thấy nó ảo thật đấy haha!!!!"
    cleaned = comment_curator.clean_text_for_tts(raw_text)
    assert "không" in cleaned
    assert "biết" in cleaned
    assert "gì" in cleaned
    assert "tôi" in cleaned
    assert "!!!!" not in cleaned

def test_comment_curator_filters_spam_and_ads():
    assert comment_curator.is_spam_or_low_quality("Mua pass đồ giá rẻ ib zalo 0987654321 freeship nha mn", 2) is True
    assert comment_curator.is_spam_or_low_quality("Tuyển ctv việc làm online kiếm 500k mỗi ngày", 0) is True
    assert comment_curator.is_spam_or_low_quality("ok", 0) is True
    assert comment_curator.is_spam_or_low_quality("Một câu chuyện rất ý nghĩa và sâu sắc của tác giả", 10) is False

def test_comment_curator_scores_humor_and_punchlines():
    humor_c = MockComment(
        id="c_humor",
        content="Đọc bài này xong mà cười bò bật ngửa luôn má ơi, bẻ lái quá gắt haha!",
        likes=120,
        replies=15
    )
    evaluated = comment_curator.evaluate_comment(humor_c)
    assert evaluated.humor_score >= 40.0
    assert evaluated.overall_score > 50.0
    assert evaluated.suggested_sfx == "punchline"
    assert "hài hước" in evaluated.selection_reason.lower()

def test_comment_curator_preserves_dialog_thread():
    parent_c = MockComment(
        id="c_parent",
        content="Hồi đó mình từng bị một vố đau đớn khi tin lời bạn thân mượn tiền.",
        likes=80
    )
    reply_c = MockComment(
        id="c_reply",
        content="Và rồi bạn nhận ra bài học: cho mượn tiền là mất cả tiền lẫn bạn đúng ko haha!",
        likes=95,
        parent_id="c_parent",
        depth=1
    )
    res = comment_curator.curate([parent_c, reply_c], target_count=5, mode="balanced")
    assert len(res.curated_comments) == 2
    assert res.total_filtered_spam == 0
    # Both parent and child reply are kept in the thread
    ids = [c.comment_id for c in res.curated_comments]
    assert "c_parent" in ids
    assert "c_reply" in ids
