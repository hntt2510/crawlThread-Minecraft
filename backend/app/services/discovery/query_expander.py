import re
import unicodedata
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel

def remove_accents(text: str) -> str:
    """Removes Vietnamese accents/diacritics for flexible fuzzy token matching."""
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    text = re.sub(r"[\u0300-\u036f]", "", text)
    text = text.replace("đ", "d").replace("Đ", "D")
    return unicodedata.normalize("NFC", text).lower()

class QueryExpansionResult(BaseModel):
    original_query: str
    unaccented_query: str
    tokens: List[str]
    search_queries: List[str]
    matched_cluster_label: Optional[str] = None
    suggested_category: Optional[str] = None
    suggested_topics: List[str] = []

# Rich semantic clusters covering Vietnamese youth & daily life interests
SEMANTIC_CLUSTERS = [
    {
        "id": "cleaning_living",
        "label": "Dọn Nhà & Đời Sống Ở Trọ",
        "category": "lifestyle",
        "trigger_keywords": [
            "giẻ", "gie", "lau", "chổi", "choi", "quét", "quet", "dọn", "don",
            "vệ sinh", "ve sinh", "nhà cửa", "nha cua", "phòng trọ", "phong tro",
            "ở trọ", "o tro", "chủ trọ", "chu tro", "giặt", "giat", "rửa bát",
            "đồ gia dụng", "do gia dung", "hút bụi", "hut bui", "khăn lau", "khan lau"
        ],
        "search_queries": ["dọn nhà", "ở trọ", "phòng trọ", "đồ gia dụng"],
        "suggested_topics": ["Dọn nhà & Đời sống ở trọ", "Kinh nghiệm thuê phòng", "Đồ gia dụng tiện ích"]
    },
    {
        "id": "relationships",
        "label": "Tình Yêu & Red Flag",
        "category": "relationships",
        "trigger_keywords": [
            "crush", "người yêu", "nguoi yeu", "ny", "ex", "tình cũ", "tinh cu",
            "cắm sừng", "cam sung", "chia tay", "hẹn hò", "hen ho", "date",
            "tỏ tình", "to tinh", "tán", "tan", "red flag", "green flag", "tinder",
            "nfl", "lụy", "luy", "yêu", "yeu", "bạn gái", "ban gai", "bạn trai", "ban trai"
        ],
        "search_queries": ["tình yêu", "hẹn hò", "red flag", "người yêu cũ"],
        "suggested_topics": ["Góc Red Flag khi yêu", "Chuyện người yêu cũ", "Confession hẹn hò"]
    },
    {
        "id": "work_office",
        "label": "Chuyện Đi Làm & Công Sở",
        "category": "business",
        "trigger_keywords": [
            "sếp", "sep", "đồng nghiệp", "dong nghiep", "công sở", "cong so",
            "đi làm", "di lam", "lương", "luong", "thưởng", "thuong", "nghỉ việc", "nghi viec",
            "nhảy việc", "nhay viec", "phỏng vấn", "phong van", "cv", "deadline", "ot",
            "toxic", "thử việc", "thu viec", "công ty", "cong ty", "intern"
        ],
        "search_queries": ["chuyện đi làm", "công sở", "drama đi làm", "sếp"],
        "suggested_topics": ["Drama đi làm & Sếp", "Nghỉ việc & Nhảy việc", "Lương bổng & Đồng nghiệp"]
    },
    {
        "id": "showbiz_entertainment",
        "label": "Showbiz & Idol",
        "category": "entertainment",
        "trigger_keywords": [
            "showbiz", "idol", "ca sĩ", "ca si", "diễn viên", "dien vien", "concert",
            "anh trai", "say hi", "rap việt", "rap viet", "phim", "mv", "scandal",
            "sao kê", "sao ke", "hóng biến", "hong bien", "bóc phốt", "boc phot"
        ],
        "search_queries": ["anh trai say hi", "showbiz", "rap việt", "hóng biến"],
        "suggested_topics": ["Anh Trai Say Hi", "Showbiz & Minh Bạch", "Rap Việt & Nhạc Trẻ"]
    },
    {
        "id": "food_dining",
        "label": "Món Ngon & Quán Xá",
        "category": "food",
        "trigger_keywords": [
            "ăn", "an", "uống", "uong", "quán", "quan", "cafe", "cà phê", "ca phe",
            "trà sữa", "tra sua", "bún", "bun", "phở", "pho", "buffet", "nấu ăn", "nau an",
            "đồ ăn", "do an", "quán xá", "quan xa", "review quán", "review quan"
        ],
        "search_queries": ["quán ăn", "quán cafe", "ẩm thực", "món ngon"],
        "suggested_topics": ["Review quán ăn ngon", "Quán cafe chill", "Món hot trend giới trẻ"]
    },
    {
        "id": "emotion_lifestyle",
        "label": "Tiểu Phẩm & Chữa Lành",
        "category": "lifestyle",
        "trigger_keywords": [
            "overthinking", "suy", "áp lực", "ap luc", "buồn", "buon", "cô đơn", "co don",
            "khóc", "khoc", "chữa lành", "chua lanh", "healing", "vô tri", "vo tri",
            "tiểu phẩm", "tieu pham", "hài", "hai", "hài hước", "hai huoc", "cười", "cuoi"
        ],
        "search_queries": ["tiểu phẩm", "overthinking", "vô tri", "chữa lành"],
        "suggested_topics": ["Tiểu phẩm hài vô tri", "Tâm sự & Overthinking", "Góc chữa lành tâm hồn"]
    },
    {
        "id": "student_education",
        "label": "Sinh Viên & Thi Cử",
        "category": "education",
        "trigger_keywords": [
            "học", "hoc", "sinh viên", "sinh vien", "thi cử", "thi cu", "kì thi", "ki thi",
            "đại học", "dai hoc", "thuyết trình", "thuyet trinh", "kí túc xá", "ki tuc xa",
            "điểm số", "diem so", "luận văn", "luan van", "học bổng", "hoc bong"
        ],
        "search_queries": ["sinh viên", "học tập", "thi cử", "kí túc xá"],
        "suggested_topics": ["Đời sống sinh viên", "Kinh nghiệm thi cử & Luận văn", "Chuyện kí túc xá"]
    },
    {
        "id": "tech_ai",
        "label": "Công Nghệ & AI Trẻ",
        "category": "technology",
        "trigger_keywords": [
            "ai", "chatgpt", "công nghệ", "cong nghe", "code", "lập trình", "lap trinh",
            "iphone", "laptop", "điện thoại", "dien thoai", "macbook", "app", "ứng dụng", "ung dung"
        ],
        "search_queries": ["công nghệ", "trí tuệ nhân tạo", "ai", "iphone"],
        "suggested_topics": ["Ứng dụng AI kiếm tiền", "Review công nghệ", "Tips sử dụng ChatGPT"]
    },
    {
        "id": "money_finance",
        "label": "Gen Z Kiếm Tiền & Tài Chính",
        "category": "business",
        "trigger_keywords": [
            "tiền", "tien", "kiếm tiền", "kiem tien", "tài chính", "tai chinh", "đầu tư", "dau tu",
            "chứng khoán", "chung khoan", "tiết kiệm", "tiet kiem", "kinh doanh", "bán hàng", "ban hang"
        ],
        "search_queries": ["kiếm tiền", "tài chính", "tiết kiệm", "đầu tư"],
        "suggested_topics": ["Gen Z học cách kiếm tiền", "Quản lý tài chính cá nhân", "Kinh doanh online"]
    },
    {
        "id": "travel_checkin",
        "label": "Phượt & Check-in",
        "category": "travel",
        "trigger_keywords": [
            "du lịch", "du lich", "phượt", "phuot", "check-in", "checkin", "khách sạn", "khach san",
            "homestay", "đà lạt", "da lat", "vũng tàu", "vung tau", "hà giang", "ha giang", "biển", "bien"
        ],
        "search_queries": ["du lịch", "check-in", "phượt", "homestay"],
        "suggested_topics": ["Lịch trình phượt Đà Lạt", "Kinh nghiệm check-in giá rẻ", "Homestay view đẹp"]
    },
    {
        "id": "sports_fitness",
        "label": "Pickleball & Fitness",
        "category": "sports",
        "trigger_keywords": [
            "gym", "pickleball", "chạy bộ", "chay bo", "fitness", "bóng đá", "bong da",
            "cầu lông", "cau long", "yoga", "tập luyện", "tap luyen", "giảm cân", "giam can"
        ],
        "search_queries": ["pickleball", "gym fitness", "chạy bộ", "thể thao"],
        "suggested_topics": ["Trào lưu Pickleball", "Hành trình giảm cân & Gym", "Chạy bộ mỗi sáng"]
    }
]

class QueryExpander:
    """Expands user search keywords into query variants and ensures strict relevance scoring."""

    def expand_query(self, keyword: str, category: Optional[str] = None) -> QueryExpansionResult:
        kw = (keyword or "").strip()
        if not kw:
            return QueryExpansionResult(
                original_query="",
                unaccented_query="",
                tokens=[],
                search_queries=[],
                matched_cluster_label=None,
                suggested_category=category or "all",
                suggested_topics=[]
            )

        kw_lower = kw.lower()
        unacc_kw = remove_accents(kw_lower)
        tokens = [t for t in re.findall(r"\b\w+\b", unacc_kw) if len(t) >= 2]

        queries_to_run: List[str] = [kw]
        if unacc_kw and unacc_kw != kw_lower:
            queries_to_run.append(unacc_kw)

        matched_cluster = None
        matched_label = None
        suggested_cat = category

        # Find matching semantic cluster
        for cluster in SEMANTIC_CLUSTERS:
            # Check full keyword or unaccented
            for trig in cluster["trigger_keywords"]:
                if trig in kw_lower or trig in unacc_kw or trig in tokens:
                    matched_cluster = cluster
                    matched_label = cluster["label"]
                    if not suggested_cat or suggested_cat == "all":
                        suggested_cat = cluster["category"]
                    break
            if matched_cluster:
                break

        suggested_topics = []
        if matched_cluster:
            for sq in matched_cluster["search_queries"]:
                if sq not in queries_to_run:
                    queries_to_run.append(sq)
            suggested_topics = matched_cluster.get("suggested_topics", [])
        else:
            # If no cluster matched, add meaningful tokens if multi-word
            if len(tokens) > 1:
                for tok in tokens[:2]:
                    if tok not in queries_to_run:
                        queries_to_run.append(tok)

        return QueryExpansionResult(
            original_query=kw,
            unaccented_query=unacc_kw,
            tokens=tokens,
            search_queries=queries_to_run[:4],
            matched_cluster_label=matched_label,
            suggested_category=suggested_cat,
            suggested_topics=suggested_topics
        )

    def calculate_relevance(
        self,
        post_content: str,
        expansion: QueryExpansionResult
    ) -> Tuple[float, str]:
        """Calculates relevance score (0 to 100) and returns human-readable reason.
        Strict rule: If score is 0.0, the post MUST NOT be displayed under this keyword search.
        """
        if not expansion.original_query:
            # No keyword search -> all posts relevant
            return 100.0, "Bài viết thịnh hành"

        if not post_content:
            return 0.0, "Nội dung trống"

        p_lower = post_content.lower()
        p_unacc = remove_accents(p_lower)
        orig_kw = expansion.original_query.lower()
        unacc_kw = expansion.unaccented_query

        # 1. Exact phrase match (Highest relevance)
        if orig_kw in p_lower:
            return 100.0, f"Khớp chính xác từ khóa: '{expansion.original_query}'"

        if unacc_kw and unacc_kw in p_unacc:
            return 92.0, f"Khớp từ khóa: '{expansion.original_query}'"

        # 2. Token match (Contains all or some words)
        matched_tokens = [tok for tok in expansion.tokens if tok in p_unacc]
        if matched_tokens:
            ratio = len(matched_tokens) / max(1, len(expansion.tokens))
            score = 65.0 + ratio * 25.0
            return round(score, 1), f"Chứa từ khóa: {', '.join(matched_tokens)}"

        # 3. Semantic cluster match
        if expansion.matched_cluster_label:
            # Check if any cluster trigger keywords are present
            for cluster in SEMANTIC_CLUSTERS:
                if cluster["label"] == expansion.matched_cluster_label:
                    cluster_hits = [t for t in cluster["trigger_keywords"] if t in p_lower or t in p_unacc]
                    if cluster_hits:
                        return 55.0, f"Chủ đề liên quan: {expansion.matched_cluster_label}"

        # 4. Absolutely no match -> DISCARD
        return 0.0, "Không liên quan từ khóa"

query_expander = QueryExpander()

