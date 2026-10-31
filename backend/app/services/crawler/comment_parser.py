import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from backend.app.services.crawler.base import CrawledComment, CrawlQualityReport

logger = logging.getLogger("studio.crawler.parser")

class RawCommentCandidate:
    """Internal candidate representation before strict validation."""
    def __init__(
        self,
        id: str,
        content: str,
        author_username: str,
        author_display_name: str = "",
        author_avatar_url: str = "",
        root_post_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        parent_author_username: Optional[str] = None,
        like_count: Optional[int] = None,
        reply_count: Optional[int] = None,
        published_at: Optional[str] = None,
        reply_level: Optional[int] = None,
        raw_code: Optional[str] = None
    ):
        self.id = str(id).strip()
        self.content = content.strip() if content else ""
        self.author_username = author_username.strip() if author_username else ""
        self.author_display_name = author_display_name.strip() if author_display_name else self.author_username
        self.author_avatar_url = author_avatar_url.strip() if author_avatar_url else ""
        self.root_post_id = str(root_post_id).strip() if root_post_id else None
        self.parent_id = str(parent_id).strip() if parent_id else None
        self.parent_author_username = str(parent_author_username).strip() if parent_author_username else None
        self.like_count = like_count
        self.reply_count = reply_count
        self.published_at = published_at
        self.reply_level = reply_level
        self.raw_code = raw_code.strip() if raw_code else None

class CommentParser:
    """Validates, deduplicates, and resolves parent-child nesting for conversation comments."""

    def parse_conversation(
        self,
        target_root_id: str,
        target_root_code: Optional[str],
        candidates: List[RawCommentCandidate],
        expected_reply_count: Optional[int] = None,
        data_source: str = "relay_cache"
    ) -> Tuple[List[CrawledComment], CrawlQualityReport]:
        
        target_root_id_str = str(target_root_id).strip().lower()
        target_root_code_str = str(target_root_code).strip().lower() if target_root_code else None

        seen_ids: Set[str] = set()
        duplicate_count = 0
        rejected_count = 0
        unresolved_count = 0

        # Filter and validate candidates
        valid_candidates: List[RawCommentCandidate] = []

        for c in candidates:
            c_id = c.id
            if not c_id:
                rejected_count += 1
                continue

            # 1. Reject if ID has already been processed (Deduplicate)
            if c_id in seen_ids:
                duplicate_count += 1
                continue

            # 2. Reject if candidate is the root post itself
            c_id_lower = c_id.lower()
            c_code_lower = c.raw_code.lower() if c.raw_code else None
            if (
                c_id_lower == target_root_id_str
                or (target_root_code_str and c_code_lower == target_root_code_str)
                or (target_root_code_str and target_root_code_str in c_id_lower)
            ):
                # This is the root post, MUST NEVER be included in comments list
                continue

            # 3. Reject if text is empty
            if not c.content:
                rejected_count += 1
                continue

            # 4. If root_post_id is present, verify it matches target_root_id
            if c.root_post_id:
                cand_root = c.root_post_id.lower()
                if (
                    cand_root != target_root_id_str
                    and (target_root_code_str and cand_root != target_root_code_str)
                ):
                    # Belongs to a different root post / unrelated conversation
                    rejected_count += 1
                    continue

            seen_ids.add(c_id)
            valid_candidates.append(c)

        # Build ID lookup map for parent relationship & nesting calculation
        cand_map: Dict[str, RawCommentCandidate] = {c.id: c for c in valid_candidates}
        final_comments: List[CrawledComment] = []
        retrieved_replies = 0

        for c in valid_candidates:
            parent_id = c.parent_id
            nesting_depth = 0

            # Determine if this replied to root post directly
            is_reply_to_root = False
            if parent_id:
                p_lower = parent_id.lower()
                if (
                    p_lower == target_root_id_str
                    or (target_root_code_str and p_lower == target_root_code_str)
                ):
                    is_reply_to_root = True
                    parent_id = None
            elif c.reply_level == 1:
                # Top level reply to root post
                is_reply_to_root = True
                parent_id = None

            # If parent_id refers to another comment
            if parent_id:
                if parent_id in cand_map:
                    # Verified parent exists in our candidate set
                    parent_cand = cand_map[parent_id]
                    # Compute depth (capped at 5 to prevent UI overflows)
                    depth = 1
                    curr_p = parent_cand
                    visited_p = {c.id, parent_id}
                    while curr_p.parent_id and curr_p.parent_id in cand_map:
                        if curr_p.parent_id in visited_p:
                            break  # cycle protection
                        visited_p.add(curr_p.parent_id)
                        depth += 1
                        curr_p = cand_map[curr_p.parent_id]
                    nesting_depth = min(depth, 5)
                    retrieved_replies += 1
                else:
                    # Unresolved parent reference
                    unresolved_count += 1
                    if c.reply_level and c.reply_level > 1:
                        nesting_depth = min(c.reply_level - 1, 3)
                        retrieved_replies += 1
                    else:
                        nesting_depth = 0
                        parent_id = None
            elif not is_reply_to_root and c.reply_level and c.reply_level > 1:
                # Indicated as nested reply by platform metadata
                nesting_depth = min(c.reply_level - 1, 3)
                retrieved_replies += 1

            comment_obj = CrawledComment(
                id=c.id,
                parent_comment_id=parent_id,
                parent_author_username=c.parent_author_username,
                author_username=c.author_username,
                author_display_name=c.author_display_name or c.author_username,
                author_avatar_url=c.author_avatar_url,
                content=c.content,
                like_count=c.like_count,
                reply_count=c.reply_count,
                nesting_depth=nesting_depth,
                published_at=c.published_at
            )
            final_comments.append(comment_obj)

        warnings: List[str] = []
        if expected_reply_count is not None and expected_reply_count > len(final_comments):
            warnings.append(
                f"Đã thu thập {len(final_comments)}/{expected_reply_count} bình luận. Một số bình luận có thể bị giới hạn hiển thị bởi Meta Threads."
            )
        if unresolved_count > 0:
            warnings.append(f"Có {unresolved_count} bình luận không thể xác định chính xác bình luận cha.")

        report = CrawlQualityReport(
            original_post_id=target_root_id,
            expected_reply_count=expected_reply_count,
            retrieved_comment_count=len(final_comments),
            retrieved_reply_count=retrieved_replies,
            duplicate_count=duplicate_count,
            rejected_record_count=rejected_count,
            unresolved_relationship_count=unresolved_count,
            data_source=data_source,
            crawl_status="success" if len(final_comments) > 0 else "partial",
            completeness_warnings=warnings
        )

        return final_comments, report

comment_parser = CommentParser()
