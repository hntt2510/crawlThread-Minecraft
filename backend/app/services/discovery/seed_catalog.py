from typing import List, Dict, Any, Optional

CATEGORIES: Dict[str, Dict[str, str]] = {
    "all": {"label": "🔥 Xu Hướng Gen Z", "icon": "Sparkles", "desc": "Tổng hợp trend nóng nhất giới trẻ: Drama, Tiểu phẩm, Tình cảm, Công sở"},
    "entertainment": {"label": "Showbiz & Idol", "icon": "Film", "desc": "Anh Trai Say Hi, Concert, Gameshow, Rap Việt, Drama nghệ sĩ"},
    "lifestyle": {"label": "Tiểu Phẩm & Đời Sống", "icon": "Smile", "desc": "Tiểu phẩm hài vô tri, Overthinking 2h sáng, Meme giới trẻ, Chữa lành"},
    "relationships": {"label": "Tình Yêu & Red Flag", "icon": "Heart", "desc": "Bóc phốt red flag, Trap boy/girl, Cắm sừng, Confession hẹn hò"},
    "society": {"label": "Chuyện Đi Làm & Công Sở", "icon": "Users", "desc": "Sếp toxic, Đồng nghiệp thảo mai, Thực tập sinh, Drama công sở, Trọ bất ổn"},
    "technology": {"label": "Công Nghệ & AI Trẻ", "icon": "Cpu", "desc": "AI làm video, Tool kiếm tiền online, Review đồ công nghệ hot, IT"},
    "business": {"label": "Gen Z Kiếm Tiền", "icon": "TrendingUp", "desc": "Lương tháng 10-20 triệu, Khởi nghiệp trẻ, Bán hàng online, Độc lập tài chính"},
    "food": {"label": "Món Hot Trend & Quán Xá", "icon": "Utensils", "desc": "Món ăn trend TikTok/Threads, Quán cà phê sống ảo, Phốt quán ăn"},
    "travel": {"label": "Phượt & Check-in", "icon": "Compass", "desc": "Đi phượt tự túc, Điểm sống ảo mới, Review homestay, Trải nghiệm độc lạ"},
    "sports": {"label": "Pickleball & Fitness", "icon": "Trophy", "desc": "Cơn sốt Pickleball, Chạy bộ Marathon trẻ, Gym flex body, Bóng đá tranh luận"},
    "education": {"label": "Sinh Viên & Thi Cử", "icon": "BookOpen", "desc": "Deadline dí, Tranh luận học đường, Unpopular opinion, Chuyện KTX"}
}

VIETNAM_SEED_TOPICS: List[Dict[str, Any]] = [
    # All / Viral Gen Z Hot Topics
    {"name": "Hóng Biến & Drama Threads", "category": "all", "traffic_hint": "Bùng nổ thảo luận", "keywords": ["hóng drama", "bóc phốt", "biến căng", "hóng hớt"]},
    {"name": "Góc Nhìn Trái Chiều (Unpopular Opinion)", "category": "all", "traffic_hint": "Nhiều tranh cãi", "keywords": ["unpopular opinion", "hỏi thật các bạn", "quan điểm cá nhân", "có ai thấy"]},
    {"name": "Tiểu Phẩm Hài Hước Vô Tri", "category": "all", "traffic_hint": "Siêu viral", "keywords": ["tiểu phẩm", "vô tri", "hài hước", "mắc cười"]},

    # Entertainment & Showbiz
    {"name": "Anh Trai Say Hi & Concert Hot", "category": "entertainment", "traffic_hint": "+150K tương tác", "keywords": ["Anh Trai Say Hi", "concert anh trai", "rhyder", "hieuthuhai", "anh trai vượt ngàn chông gai"]},
    {"name": "Rap Việt & Nhạc Trẻ Thịnh Hành", "category": "entertainment", "traffic_hint": "Rất hot", "keywords": ["Rap Việt", "nhạc trending", "vpop", "suboi", "karik"]},
    {"name": "Review Phim Rạp & Drama Showbiz", "category": "entertainment", "traffic_hint": "Thảo luận cao", "keywords": ["review phim", "phim chiếu rạp", "drama showbiz việt"]},

    # Lifestyle & Gen Z
    {"name": "Overthinking 2 Giờ Sáng", "category": "lifestyle", "traffic_hint": "Đồng cảm cao", "keywords": ["overthinking", "tâm sự đêm khuya", "suy nghĩ nhiều", "trầm cảm tuổi 20"]},
    {"name": "Tiểu Phẩm Gen Z & Tình Huống Éo Le", "category": "lifestyle", "traffic_hint": "Hài hước", "keywords": ["tiểu phẩm gen z", "tình huống éo le", "hài hước vô tri"]},
    {"name": "Chữa Lành Hay Tổn Thương", "category": "lifestyle", "traffic_hint": "Xu hướng", "keywords": ["chữa lành", "áp lực đồng trang lứa", "peer pressure", "sống một mình"]},

    # Relationships & Dating
    {"name": "Góc Red Flag - Green Flag Khi Yêu", "category": "relationships", "traffic_hint": "Tranh luận nảy lửa", "keywords": ["red flag", "green flag", "thao túng tâm lý", "toxic relationship"]},
    {"name": "Chuyện Người Yêu Cũ & Cắm Sừng", "category": "relationships", "traffic_hint": "Triệu view", "keywords": ["người yêu cũ", "cắm sừng", "bạn thân người yêu", "trap boy"]},
    {"name": "Confession Hẹn Hò Tinder & Threads", "category": "relationships", "traffic_hint": "Tương tác khủng", "keywords": ["hẹn hò", "tinder việt nam", "match threads", "first date"]},

    # Society & Workplace
    {"name": "Gen Z Đi Làm & Sếp Toxic", "category": "society", "traffic_hint": "Đồng cảm sâu sắc", "keywords": ["gen z đi làm", "sếp toxic", "drama công sở", "nghỉ việc", "thực tập sinh"]},
    {"name": "Kiếp Đi Làm Thuê & Lương Bổng", "category": "society", "traffic_hint": "Thảo luận nóng", "keywords": ["lương bổng", "deadline", "nhảy việc", "đi làm áp lực"]},
    {"name": "Kiếp Thuê Trọ Bất Ổn & KTX", "category": "society", "traffic_hint": "Phốt cực căng", "keywords": ["thuê trọ bất ổn", "bạn cùng phòng", "chủ trọ", "ktx sinh viên"]},

    # Technology & AI
    {"name": "Tool AI Làm Video & Mẹo Kiếm Tiền", "category": "technology", "traffic_hint": "Cực hot", "keywords": ["AI làm video", "tool AI", "ChatGPT", "kiếm tiền online AI"]},
    {"name": "Review iPhone & Phụ Kiện Sống Ảo", "category": "technology", "traffic_hint": "Quan tâm cao", "keywords": ["iPhone", "review công nghệ", "đồ công nghệ gen z"]},
    {"name": "Chuyện Dân IT & Lập Trình Viên Trẻ", "category": "technology", "traffic_hint": "Nhiều meme", "keywords": ["lập trình viên", "dân IT", "học code", "ngành IT"]},

    # Business & Money
    {"name": "Gen Z Kiếm Tiền & Độc Lập Tài Chính", "category": "business", "traffic_hint": "Xu hướng trẻ", "keywords": ["gen z kiếm tiền", "tài chính tuổi 20", "tiết kiệm tiền", "thu nhập hàng tháng"]},
    {"name": "Khởi Nghiệp Nhỏ & Bán Hàng Online", "category": "business", "traffic_hint": "Đang lên", "keywords": ["bán hàng online", "khởi nghiệp nhỏ", "kinh doanh tự do"]},

    # Food & Hot Trends
    {"name": "Món Ăn Trend & Review Quán Xá", "category": "food", "traffic_hint": "Hot TikTok", "keywords": ["món hot trend", "quán ăn ngon", "review ăn uống", "street food"]},
    {"name": "Cà Phê Sống Ảo & Check-in Gen Z", "category": "food", "traffic_hint": "Phổ biến", "keywords": ["cà phê sống ảo", "cafe tone đen", "quán cafe đẹp"]},

    # Travel & Experiences
    {"name": "Du Lịch Tự Túc & Đi Phượt Chữa Lành", "category": "travel", "traffic_hint": "Check-in hot", "keywords": ["du lịch tự túc", "phượt đà lạt", "check in hà giang", "đi chơi chữa lành"]},
    {"name": "Review Homestay & Cảnh Báo Phốt", "category": "travel", "traffic_hint": "Cảnh giác", "keywords": ["review homestay", "phốt du lịch", "kinh nghiệm đi chơi"]},

    # Sports & Trends
    {"name": "Cơn Sốt Pickleball Giới Trẻ", "category": "sports", "traffic_hint": "Rất hot", "keywords": ["pickleball việt nam", "sân pickleball", "trang phục pickleball"]},
    {"name": "Chạy Bộ Marathon & Gym Flex Body", "category": "sports", "traffic_hint": "Trend năng động", "keywords": ["chạy bộ", "marathon trẻ", "gym flex", "tập gym"]},

    # Education & Campus Life
    {"name": "Deadline Ngập Đầu & Cuộc Sống Đại Học", "category": "education", "traffic_hint": "Meme sinh viên", "keywords": ["deadline ngập đầu", "sinh viên đại học", "thi cử", "học bổng"]},
    {"name": "Unpopular Opinion Về Chọn Ngành Học", "category": "education", "traffic_hint": "Nhiều tranh cãi", "keywords": ["chọn ngành học", "đại học hay đi làm", "du học sinh"]}
]

class VietnamTopicSeedProvider:
    """Provides curated Vietnam discovery seeds, categories, and keyword catalogs tuned for Gen Z viral trends."""

    @staticmethod
    def get_categories() -> Dict[str, Dict[str, str]]:
        return CATEGORIES

    @staticmethod
    def get_seeds(category: Optional[str] = None) -> List[Dict[str, Any]]:
        if not category or category == "all":
            return VIETNAM_SEED_TOPICS
        return [t for t in VIETNAM_SEED_TOPICS if t.get("category") == category]

    @staticmethod
    def get_search_queries_for_topic(topic_name: str) -> List[str]:
        for t in VIETNAM_SEED_TOPICS:
            if t["name"].lower() == topic_name.lower():
                return t.get("keywords", [topic_name])
        return [topic_name]

vietnam_topic_seed_provider = VietnamTopicSeedProvider()
