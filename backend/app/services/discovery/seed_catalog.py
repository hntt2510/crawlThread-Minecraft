from typing import List, Dict, Any, Optional

CATEGORIES: Dict[str, Dict[str, str]] = {
    "all": {"label": "Tất cả chủ đề", "icon": "Sparkles", "desc": "Tổng hợp xu hướng và đề xuất hot nhất"},
    "entertainment": {"label": "Giải trí & Showbiz", "icon": "Film", "desc": "Nhạc Việt, gameshow, concert và sao Việt"},
    "lifestyle": {"label": "Đời sống & Gen Z", "icon": "Smile", "desc": "Góc nhìn cuộc sống, chữa lành, tâm sự giới trẻ"},
    "technology": {"label": "Công nghệ & AI", "icon": "Cpu", "desc": "Trí tuệ nhân tạo, thiết bị số, lập trình và đổi mới"},
    "society": {"label": "Xã hội & Cộng đồng", "icon": "Users", "desc": "Chuyện công sở, văn hóa mạng, tin thảo luận nóng"},
    "business": {"label": "Kinh doanh & Tài chính", "icon": "TrendingUp", "desc": "Khởi nghiệp, đầu tư, quản lý tài chính cá nhân"},
    "food": {"label": "Ẩm thực & Quán xá", "icon": "Utensils", "desc": "Món ngon ba miền, cà phê, review ăn uống"},
    "travel": {"label": "Du lịch & Trải nghiệm", "icon": "Compass", "desc": "Khám phá Việt Nam, phượt, điểm check-in hấp dẫn"},
    "sports": {"label": "Thể thao & Fitness", "icon": "Trophy", "desc": "Bóng đá Việt Nam, pickleball, gym và chạy bộ"},
    "education": {"label": "Giáo dục & Kỹ năng", "icon": "BookOpen", "desc": "Du học, phương pháp học tập, sách hay mỗi ngày"},
    "relationships": {"label": "Tình yêu & Tâm sự", "icon": "Heart", "desc": "Chuyện hẹn hò, gia đình, bạn bè và thấu hiểu"}
}

VIETNAM_SEED_TOPICS: List[Dict[str, Any]] = [
    # Entertainment
    {"name": "Rap Việt Mùa 4", "category": "entertainment", "traffic_hint": "Rất hot", "keywords": ["Rap Việt", "rap viet mùa 4", "suboi", "karik"]},
    {"name": "Anh Trai Say Hi & Vượt Ngàn Chông Gai", "category": "entertainment", "traffic_hint": "+100K tương tác", "keywords": ["Anh Trai Say Hi", "Anh Trai Vượt Ngàn Chông Gai", "concert anh trai"]},
    {"name": "Phim Rạp Việt Nam Mới", "category": "entertainment", "traffic_hint": "Thảo luận sôi nổi", "keywords": ["review phim rạp", "phim chiếu rạp", "điện ảnh việt"]},
    {"name": "Nhạc Việt Thịnh Hành", "category": "entertainment", "traffic_hint": "Xu hướng", "keywords": ["nhạc việt", "vpop trending", "ca khúc mới"]},

    # Lifestyle
    {"name": "Lối Sống Chữa Lành & Tối Giản", "category": "lifestyle", "traffic_hint": "Đang tăng", "keywords": ["chữa lành", "lối sống tối giản", "cân bằng cuộc sống"]},
    {"name": "Gen Z Đi Làm & Chuyện Công Sở", "category": "lifestyle", "traffic_hint": "Nhiều tranh luận", "keywords": ["gen z đi làm", "chuyện công sở", "drama công sở", "nghỉ việc"]},
    {"name": "Thói Quen Buổi Sáng Tích Cực", "category": "lifestyle", "traffic_hint": "Truyền cảm hứng", "keywords": ["thói quen sống", "dậy sớm", "kỷ luật bản thân"]},

    # Technology
    {"name": "Trí Tuệ Nhân Tạo & Ứng Dụng Hàng Ngày", "category": "technology", "traffic_hint": "+50K tìm kiếm", "keywords": ["trí tuệ nhân tạo", "AI việt nam", "ChatGPT", "công nghệ mới"]},
    {"name": "Review Smartphone & Laptop Mới", "category": "technology", "traffic_hint": "Hot", "keywords": ["iPhone", "MacBook", "review đồ công nghệ", "smartphone"]},
    {"name": "Học Lập Trình & Nghề Tech", "category": "technology", "traffic_hint": "Đang quan tâm", "keywords": ["lập trình viên", "học code", "ngành IT việt nam"]},

    # Society
    {"name": "Chuyện Thuê Nhà & Giá Nhà Thành Phố", "category": "society", "traffic_hint": "Thảo luận cao", "keywords": ["thuê nhà hà nội", "thuê trọ sài gòn", "mua nhà", "chi phí sinh hoạt"]},
    {"name": "Văn Hóa Mạng Xã Hội Hiện Nay", "category": "society", "traffic_hint": "Góc nhìn", "keywords": ["mạng xã hội", "văn hóa ứng xử", "threads việt nam"]},

    # Business
    {"name": "Khởi Nghiệp Nhỏ & Bán Hàng Online", "category": "business", "traffic_hint": "Xu hướng", "keywords": ["khởi nghiệp", "bán hàng online", "kinh doanh nhỏ", "ecommerce"]},
    {"name": "Quản Lý Tài Chính Tuổi 25-30", "category": "business", "traffic_hint": "Quan tâm cao", "keywords": ["tài chính cá nhân", "tiết kiệm tiền", "đầu tư tích lũy"]},

    # Food
    {"name": "Món Ngon Đường Phố & Ăn Đêm", "category": "food", "traffic_hint": "+80K tương tác", "keywords": ["món ngon hà nội", "ăn vặt sài gòn", "quán ăn ngon", "street food việt nam"]},
    {"name": "Cà Phê Sống Ảo & Không Gian Đẹp", "category": "food", "traffic_hint": "Phổ biến", "keywords": ["quán cà phê đẹp", "cafe sống ảo", "review cà phê"]},

    # Travel
    {"name": "Mùa Du Lịch & Địa Điểm Check-in Mới", "category": "travel", "traffic_hint": "Đang thịnh hành", "keywords": ["du lịch việt nam", "đà lạt", "hà giang", "điểm check in đẹp"]},
    {"name": "Kinh Nghiệm Du Lịch Tự Túc", "category": "travel", "traffic_hint": "Hữu ích", "keywords": ["du lịch tự túc", "review chuyến đi", "homestay đẹp"]},

    # Sports
    {"name": "Phong Trào Chạy Bộ & Marathon Việt Nam", "category": "sports", "traffic_hint": "Đang lên", "keywords": ["chạy bộ", "marathon việt nam", "chạy 5k", "chạy 10k"]},
    {"name": "Cơn Sốt Pickleball Giới Trẻ", "category": "sports", "traffic_hint": "Rất hot", "keywords": ["pickleball việt nam", "chơi pickleball", "sân pickleball"]},
    {"name": "Bóng Đá Việt Nam & Ngoại Hạng Anh", "category": "sports", "traffic_hint": "Cuối tuần sôi động", "keywords": ["bóng đá việt nam", "ngoại hạng anh", "tin tức bóng đá"]},

    # Education
    {"name": "Học Ngoại Ngữ & Thi IELTS", "category": "education", "traffic_hint": "Quan tâm bền vững", "keywords": ["học tiếng anh", "ôn thi ielts", "kỹ năng tự học"]},
    {"name": "Sách Hay Thay Đổi Tư Duy", "category": "education", "traffic_hint": "Gợi ý tốt", "keywords": ["sách hay nên đọc", "review sách", "phát triển bản thân"]},

    # Relationships
    {"name": "Góc Nhìn Hẹn Hò & Green Flag - Red Flag", "category": "relationships", "traffic_hint": "Tương tác rất cao", "keywords": ["chuyện hẹn hò", "green flag", "red flag", "tình yêu"]},
    {"name": "Cân Bằng Giữa Công Việc Và Gia Đình", "category": "relationships", "traffic_hint": "Sâu sắc", "keywords": ["gia đình", "tâm sự cuộc sống", "hạnh phúc gia đình"]}
]

class VietnamTopicSeedProvider:
    """Provides curated Vietnam discovery seeds, categories, and keyword catalogs."""

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
