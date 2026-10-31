import pytest
from backend.app.services.crawler.comment_parser import CommentParser, RawCommentCandidate

def test_comment_parser_strict_validation():
    parser = CommentParser()

    root_id = "post_root_123"
    root_code = "DeZgeQhm6RW"

    candidates = [
        # 1. The root post itself accidentally included in raw stream
        RawCommentCandidate(
            id="post_root_123",
            content="Nội dung bài viết gốc",
            author_username="zuck",
            raw_code="DeZgeQhm6RW"
        ),
        # 2. Valid top-level comment
        RawCommentCandidate(
            id="cmt_001",
            content="Bình luận số 1 rất hay!",
            author_username="user_a",
            root_post_id="post_root_123",
            parent_id="post_root_123",
            like_count=15,
            reply_count=2,
            reply_level=1
        ),
        # 3. Valid nested reply to cmt_001
        RawCommentCandidate(
            id="cmt_002",
            content="Đồng ý với user_a luôn nè",
            author_username="user_b",
            root_post_id="post_root_123",
            parent_id="cmt_001",
            like_count=5,
            reply_level=2
        ),
        # 4. Deeply nested reply to cmt_002
        RawCommentCandidate(
            id="cmt_003",
            content="Chuẩn không cần chỉnh",
            author_username="user_c",
            root_post_id="post_root_123",
            parent_id="cmt_002",
            like_count=None,  # Missing metrics should stay None
            reply_level=3
        ),
        # 5. Comment from original author (zuck) replying to a fan
        RawCommentCandidate(
            id="cmt_004",
            content="Cảm ơn bạn nhé!",
            author_username="zuck",
            root_post_id="post_root_123",
            parent_id="cmt_001",
            like_count=100,
            reply_level=2
        ),
        # 6. Duplicate of cmt_001
        RawCommentCandidate(
            id="cmt_001",
            content="Bình luận số 1 rất hay!",
            author_username="user_a",
            root_post_id="post_root_123"
        ),
        # 7. Unrelated post from a different thread
        RawCommentCandidate(
            id="unrelated_999",
            content="Bài viết ở group khác",
            author_username="stranger",
            root_post_id="other_root_99999"
        ),
        # 8. Unresolved parent (points to a comment not in thread)
        RawCommentCandidate(
            id="cmt_005",
            content="Bình luận mồ côi",
            author_username="user_d",
            root_post_id="post_root_123",
            parent_id="non_existent_cmt_id",
            reply_level=2
        ),
        # 9. Empty text comment (e.g. broken media sticker)
        RawCommentCandidate(
            id="cmt_empty",
            content="   ",
            author_username="user_e",
            root_post_id="post_root_123"
        )
    ]

    comments, report = parser.parse_conversation(
        target_root_id=root_id,
        target_root_code=root_code,
        candidates=candidates,
        expected_reply_count=10,
        data_source="relay_cache"
    )

    # Verifications:
    # 1. Root post excluded from comments
    assert all(c.id != "post_root_123" for c in comments)
    assert all(c.content != "Nội dung bài viết gốc" for c in comments)

    # 2. Unrelated post excluded
    assert all(c.id != "unrelated_999" for c in comments)

    # 3. Empty text comment excluded
    assert all(c.id != "cmt_empty" for c in comments)

    # 4. Duplicates removed (only one cmt_001)
    cmt_001_matches = [c for c in comments if c.id == "cmt_001"]
    assert len(cmt_001_matches) == 1
    assert cmt_001_matches[0].nesting_depth == 0
    assert cmt_001_matches[0].parent_comment_id is None
    assert cmt_001_matches[0].like_count == 15

    # 5. Nested replies correctly linked and calculated
    cmt_002_matches = [c for c in comments if c.id == "cmt_002"]
    assert len(cmt_002_matches) == 1
    assert cmt_002_matches[0].parent_comment_id == "cmt_001"
    assert cmt_002_matches[0].nesting_depth == 1

    cmt_003_matches = [c for c in comments if c.id == "cmt_003"]
    assert len(cmt_003_matches) == 1
    assert cmt_003_matches[0].parent_comment_id == "cmt_002"
    assert cmt_003_matches[0].nesting_depth == 2
    # Missing metrics must remain None (NOT 0)
    assert cmt_003_matches[0].like_count is None

    # 6. Author reply included as valid comment
    cmt_004_matches = [c for c in comments if c.id == "cmt_004"]
    assert len(cmt_004_matches) == 1
    assert cmt_004_matches[0].author_username == "zuck"
    assert cmt_004_matches[0].content == "Cảm ơn bạn nhé!"
    assert cmt_004_matches[0].nesting_depth == 1

    # 7. Unresolved parent counted in quality report
    assert report.unresolved_relationship_count >= 1

    # 8. Report statistics accurate
    assert report.duplicate_count == 1
    assert report.rejected_record_count >= 2  # unrelated + empty
    assert report.retrieved_comment_count == len(comments)
    assert report.retrieved_reply_count >= 3  # cmt_002, cmt_003, cmt_004, cmt_005
    assert report.original_post_id == root_id
    assert report.data_source == "relay_cache"
