# UI/UX Specification — Threads Comment Video Studio

## 1. Visual Design Principles & Aesthetics
- **Theme**: Modern creator dark studio theme (Slate / Zinc 900 background, crisp borders, violet/indigo accent glows, high-contrast readable typography).
- **Default Language**: Vietnamese (Tiếng Việt) with clear terminology and zero machine-translation awkwardness.
- **Form Factors**: Desktop-first layout optimized for 1920x1080 and ultrawide displays.

---

## 2. Information Architecture & Navigation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🎬 Threads Comment Video Studio                       [● Server Online]     │
├───────────────┬─────────────────────────────────────────────────────────────┤
│ 📊 Dashboard  │                                                             │
│ ➕ Dự án mới  │  Step 1: Nhập Threads URL                                    │
│ 📁 Dự án của tôi  Step 2: Quản lý & Lọc Bình Luận                           │
│ 🗃️ Kho Media  │  Step 3: Phòng Thu Giọng Đọc (TTS)                          │
│ 🚀 Xuất Bản   │  Step 4: Cấu Hình Video (Minecraft 9:16)                     │
│ 🔑 Tài Khoản  │  Step 5: Xuất Video & Dự Án CapCut                          │
│ ⚙️ Cài Đặt   │  Step 6: Đăng Lên Shorts / Reels / TikTok                   │
└───────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Workflow Steps Breakdown

### Bước 1 — Nhập Threads (Import Threads)
- Input field with automatic regex validation for Threads URLs.
- Crawl options (max comments, recursive replies toggle).
- Live crawl status card showing:
  - Original post preview (author, avatar, text, like count, media).
  - Crawl progress bar and counter (Total comments discovered, top-level vs nested replies).

### Bước 2 — Quản Lý Bình Luận (Comment Management)
- Quick Filter toolbar:
  - "Chọn nhanh Top 3", "Top 5", "Top 10" theo Lượt thích.
  - Sắp xếp: Nhiều like nhất, Nhiều phản hồi nhất, Mới nhất.
  - Lọc: Tất cả, Chỉ bình luận gốc, Chỉ phản hồi con.
- Structured Interactive Table / Card List:
  - Checkbox selection with live count badge ("Đã chọn 5/38 bình luận").
  - Drag handle to reorder scene sequence.
  - Dual text boxes for each item:
    1. **Nội dung hiển thị (Display Text)**: Văn bản xuất hiện trên thẻ video.
    2. **Lời đọc giọng đọc (TTS Text)**: Văn bản để máy đọc (viết tắt thành từ đầy đủ, thêm dấu ngắt câu, phát âm chuẩn).
  - Button "Khôi phục gốc" (Restore original text) and "Xóa khỏi danh sách".

### Bước 3 — Phòng Thu Giọng Đọc (Vietnamese Voice Studio)
- Provider selector: Edge TTS (Miễn phí, Khuyên dùng), FPT.AI, Google Cloud.
- Voice selector dropdown with Vietnamese accent tags (Bắc, Nam, Nữ truyền cảm, Nam trầm ấm).
- "Nghe thử giọng" (Live audio preview with waveform visualization).
- Global speed slider (0.8x -> 1.5x) and volume slider.
- Per-comment voice override toggle.
- "Tạo toàn bộ giọng đọc" button with real-time generation progress.

### Bước 4 — Cấu Hình Video (Video Settings)
- Minecraft Gameplay Background Selector with visual preview player.
- Background video start time selector (offset scrubber) and loop mode.
- Audio balance controls:
  - Voice volume (Default: 100%).
  - Background music volume (Default: 20%).
  - Audio Ducking toggle (tự động giảm nhỏ nhạc nền khi có tiếng nói).
- Card visual appearance: Dark card / Light card / Threads classic style.

### Bước 5 — Xuất Video & Dự Án CapCut (Export)
- Two primary action cards:
  1. **Xuất Video MP4 Hoàn Thiện**:
     - Embedded HTML5 vertical video player for instant review.
     - One-click Download MP4 button.
  2. **Xuất Dự Án CapCut Desktop (Có thể chỉnh sửa)**:
     - Badge "Đã tạo thành công thư mục CapCut Desktop".
     - Button "Mở trong CapCut Desktop" (Direct path linking to `%LOCALAPPDATA%\CapCut\...`).
     - Button "Tải gói bàn giao CapCut (.ZIP)" (Contains all assets + draft + import script for other computers).

### Bước 6 — Đăng Video (Publish Center)
- Platform selector tabs: YouTube Shorts, Facebook Page Reels, TikTok.
- Metadata editor: Title, Description, Hashtags, Privacy level (Công khai, Riêng tư, Không công khai).
- Explicit publishing confirmation modal ("Xác nhận đăng tải video").
- Progress bar and direct link to the published video upon completion.
