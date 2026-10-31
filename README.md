# Threads Comment Video Studio 🎬

> **Local-First Vertical Video Studio for Digital Creators**  
> Chuyển đổi bất kỳ bài viết Threads nào thành video ngắn 9:16 trên nền Minecraft gameplay với giọng đọc thuyết minh tiếng Việt chuẩn, xuất file dự án CapCut Desktop đa track (Multi-track) có thể chỉnh sửa và xuất bản trực tiếp lên YouTube Shorts, Facebook Page Reels và TikTok.

---

## 🌟 Tính Năng Nổi Bật (Key Capabilities)

- ⚡ **Thu Thập Threads Siêu Tốc (Relay Stream Cache)**: Trích xuất bài viết gốc và bình luận kèm lượt thích, phản hồi trong < 1 giây trực tiếp từ URL Threads mà không cần tài khoản hay trình duyệt giả lập nặng nề.
- 💬 **Quản Lý Bình Luận Chuyên Nghiệp (Dual-Text Editor)**: Tách biệt **Nội dung hiển thị (Display Text)** trên thẻ video và **Lời đọc thuyết minh (TTS Text)** cho voiceover. Hỗ trợ chọn nhanh Top 3, Top 5, Top 10 theo lượt thích, lọc bình luận con và đổi thứ tự phân cảnh.
- 🎙️ **Phòng Thu Giọng Đọc Tiếng Việt (Vietnamese Voice Studio)**: Tích hợp sẵn Microsoft Edge TTS Neural (`Hoài My` nữ truyền cảm, `Nam Minh` nam trầm ấm) hoàn toàn miễn phí, không tốn credit, kèm bộ điều khiển tốc độ (0.8x – 1.4x), bộ nhớ đệm SHA256 và adapter mở rộng cho FPT.AI / Google Cloud.
- 🎮 **Dựng Video 9:16 Tự Động (FFmpeg Engine)**: Tự động ghép thẻ bình luận bo tròn góc, drop-shadow trên nền Minecraft gameplay, trộn âm thanh giọng đọc và tự động giảm âm lượng nhạc nền (Audio Ducking -14dB) khi có tiếng nói.
- ✂️ **Xuất Dự Án CapCut Desktop Đa Track**: Tạo bản nháp CapCut Desktop Windows nguyên bản với các track riêng biệt:
  - `V1`: Video nền Gameplay.
  - `V2`: Thẻ hình ảnh bài viết gốc.
  - `V3`: Thẻ hình ảnh bình luận.
  - `A1`: Giọng đọc thuyết minh TTS.
  - `A2`: Nhạc nền BGM.
  - Tự động copy thẳng vào `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft` và đóng gói file `.zip` bàn giao độc lập kèm script import cho máy khác.
- 🚀 **Trung Tâm Xuất Bản (Publish Center)**: Đăng tải video lên YouTube Shorts, Facebook Page Reels và TikTok với xác nhận bảo mật rõ ràng.

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Động Nhanh (Windows 10/11)

### Yêu Cầu Hệ Thống:
- Windows 10 hoặc Windows 11 (64-bit)
- Python 3.12+
- Node.js v18+
- FFmpeg (đã thêm vào Windows `PATH`)
- CapCut Desktop (tùy chọn nếu muốn mở chỉnh sửa trực tiếp)

### Khởi Động 1 Click:
Chỉ cần nhấp đúp vào file:
```powershell
.\run_studio.bat
```
Hoặc chạy trong PowerShell:
```powershell
.\run_studio.ps1
```
Trình duyệt sẽ tự động mở tại địa chỉ: `http://localhost:8000`.

---

## 🏗️ Cấu Trúc Thư Mục Dự Án

```
crawlTHREAD/
├── backend/
│   ├── app/
│   │   ├── api/             # REST Routers (projects, threads, comments, tts, render, capcut, publishing)
│   │   ├── core/            # Config, database WAL, persistent job manager
│   │   ├── models/          # SQLAlchemy 2.0 ORM models
│   │   ├── schemas/         # Pydantic v2 schemas
│   │   └── services/
│   │       ├── crawler/     # Threads Relay cache & GraphQL crawler
│   │       ├── tts/         # Multi-provider Vietnamese TTS (Edge TTS, FPT.AI, Google)
│   │       ├── card_renderer/ # PIL card generator with Vietnamese Unicode typography
│   │       ├── video_composer/ # FFmpeg 9:16 vertical video & audio ducking engine
│   │       ├── capcut_exporter/ # pyCapCut multi-track builder & Windows metadata patcher
│   │       └── publishing/  # YouTube, Facebook Reels, TikTok publishers
│   └── main.py              # FastAPI app & static SPA server
├── frontend/
│   ├── src/
│   │   ├── components/      # Sidebar, Header, Stepper 1-6
│   │   ├── pages/           # Dashboard, Studio, Media Library, Accounts, Settings
│   │   ├── api/             # Frontend API client
│   │   └── types/           # TypeScript definitions
│   └── dist/                # Pre-built production SPA
├── docs/                    # PRD, Architecture, Database ERD, API specs, Decision log
├── tests/                   # Automated pytest suite (14/14 tests passing)
├── requirements.txt         # Pinned python packages
├── run_studio.ps1           # Windows startup script
└── README.md
```

---

## 🧪 Kết Quả Kiểm Thử (Test Evidence)

Chạy bộ kiểm thử tự động toàn diện:
```powershell
$env:PYTHONPATH = "."
.\.venv\Scripts\python.exe -m pytest -v
```
Kết quả kiểm thử:
```
tests/test_api_endpoints.py::test_health_check_endpoint PASSED           [  7%]
tests/test_api_endpoints.py::test_project_crud PASSED                    [ 14%]
tests/test_api_endpoints.py::test_tts_voices_endpoint PASSED             [ 21%]
tests/test_capcut_exporter.py::test_capcut_exporter_structure PASSED     [ 28%]
tests/test_card_generator.py::test_card_generator_creates_valid_png PASSED [ 35%]
tests/test_crawler_quick.py::test_crawler_live PASSED                    [ 42%]
tests/test_e2e_workflow.py::test_full_studio_workflow_integration PASSED [ 50%]
tests/test_publishing_adapters.py::test_publishing_service_validation PASSED [ 57%]
tests/test_threads_crawler.py::test_parse_threads_url_valid PASSED       [ 64%]
tests/test_threads_crawler.py::test_parse_threads_url_invalid PASSED     [ 71%]
tests/test_threads_crawler.py::test_crawler_html_parsing_synthetic PASSED [ 78%]
tests/test_tts_service.py::test_tts_voices_list PASSED                   [ 85%]
tests/test_tts_service.py::test_tts_synthesis_and_caching PASSED         [ 92%]
tests/test_video_composer.py::test_video_composer_full_render PASSED     [100%]
======================= 14 passed in 5.78s =======================
```

---

## 📑 Tài Liệu Kỹ Thuật (Architecture & Specifications)
Xem thêm chi tiết tại thư mục `/docs/`:
- [Product Requirements Document](file:///d:/HOCTAP/latvat/crawlTHREAD/docs/product-requirements.md)
- [System Architecture](file:///d:/HOCTAP/latvat/crawlTHREAD/docs/system-architecture.md)
- [Database Design & ERD](file:///d:/HOCTAP/latvat/crawlTHREAD/docs/database-design.md)
- [API Specification](file:///d:/HOCTAP/latvat/crawlTHREAD/docs/api-specification.md)
- [Integration Matrix](file:///d:/HOCTAP/latvat/crawlTHREAD/docs/integration-matrix.md)
- [UI/UX Specification](file:///d:/HOCTAP/latvat/crawlTHREAD/docs/ui-ux-specification.md)
- [Testing Strategy](file:///d:/HOCTAP/latvat/crawlTHREAD/docs/testing-strategy.md)
- [Deployment Guide](file:///d:/HOCTAP/latvat/crawlTHREAD/docs/deployment-guide.md)
- [Architectural Decision Log](file:///d:/HOCTAP/latvat/crawlTHREAD/docs/decision-log.md)

---

## 🔒 Giấy Phép & Bảo Mật
Sản phẩm được phát triển tuân thủ nghiêm ngặt các nguyên tắc bảo mật: không lưu mật khẩu mạng xã hội, xác thực OAuth 2.0 an toàn, token được mã hóa cục bộ và không xuất bản nội dung nếu không có sự phê duyệt trực tiếp của người dùng.
