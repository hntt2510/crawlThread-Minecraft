import os
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

class CardGenerator:
    """Generates high-resolution social media comment cards optimized for 9:16 vertical video overlays."""

    def __init__(self):
        # Resolve best available font on Windows
        windir = os.environ.get("WINDIR", "C:\\Windows")
        fonts_dir = Path(windir) / "Fonts"
        
        self.font_regular_path = str(fonts_dir / "segoeui.ttf")
        if not Path(self.font_regular_path).exists():
            self.font_regular_path = str(fonts_dir / "arial.ttf")

        self.font_bold_path = str(fonts_dir / "segoeuib.ttf")
        if not Path(self.font_bold_path).exists():
            self.font_bold_path = str(fonts_dir / "arialbd.ttf")

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        p = self.font_bold_path if bold else self.font_regular_path
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            return ImageFont.load_default()

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
        words = text.split()
        if not words:
            return [""]
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        if current_line:
            lines.append(" ".join(current_line))
        return lines

    def create_card(
        self,
        author_username: str,
        author_display_name: str,
        content: str,
        output_path: Path,
        card_type: str = "comment",  # "post" or "comment"
        like_count: Optional[int] = None,
        reply_count: Optional[int] = None,
        theme: str = "dark",         # "dark" or "glass"
        card_width: int = 940,
    ) -> Path:
        """Create a styled card image with transparent padding for video overlay."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        padding_x = 44
        padding_y = 36
        content_width = card_width - (padding_x * 2)

        # Fonts
        font_name = self._get_font(34, bold=True)
        font_handle = self._get_font(26, bold=False)
        font_badge = self._get_font(22, bold=True)
        font_content = self._get_font(38, bold=False)
        font_footer = self._get_font(26, bold=False)

        # Dummy draw for text measurement
        dummy_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        draw_measure = ImageDraw.Draw(dummy_img)

        # Wrap content
        lines = self._wrap_text(content, font_content, content_width, draw_measure)
        line_height = 54
        content_box_height = len(lines) * line_height

        # Card total height
        header_height = 80
        footer_height = 55
        card_height = padding_y + header_height + 20 + content_box_height + 20 + footer_height + padding_y

        # Colors based on theme
        if theme == "glass":
            bg_color = (24, 24, 27, 235)      # Dark zinc glass
            border_color = (63, 63, 70, 200)
            text_color = (255, 255, 255, 255)
            subtext_color = (161, 161, 170, 255)
        else:
            bg_color = (18, 18, 20, 248)       # Rich deep dark
            border_color = (45, 45, 52, 255)
            text_color = (255, 255, 255, 255)
            subtext_color = (160, 160, 170, 255)

        # Create RGBA Image
        img = Image.new("RGBA", (card_width, card_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw rounded card rectangle
        corner_radius = 32
        draw.rounded_rectangle(
            [(0, 0), (card_width - 1, card_height - 1)],
            radius=corner_radius,
            fill=bg_color,
            outline=border_color,
            width=2
        )

        curr_y = padding_y

        # 1. Header: Avatar Circle + Names + Type Badge
        avatar_size = 64
        avatar_box = [(padding_x, curr_y), (padding_x + avatar_size, curr_y + avatar_size)]
        # Deterministic avatar background color based on username
        avatar_hue_val = sum(ord(c) for c in (author_username or "user")) % 3
        avatar_bg = [(59, 130, 246, 255), (168, 85, 247, 255), (16, 185, 129, 255)][avatar_hue_val]
        draw.ellipse(avatar_box, fill=avatar_bg)
        
        # Initial letter in avatar
        initial = (author_display_name or author_username or "U")[0].upper()
        font_initial = self._get_font(32, bold=True)
        ibox = draw.textbbox((0, 0), initial, font=font_initial)
        iw = ibox[2] - ibox[0]
        ih = ibox[3] - ibox[1]
        draw.text(
            (padding_x + (avatar_size - iw) // 2, curr_y + (avatar_size - ih) // 2 - 3),
            initial,
            fill=(255, 255, 255, 255),
            font=font_initial
        )

        # Names
        text_x = padding_x + avatar_size + 20
        name_str = author_display_name or author_username or "Người dùng"
        draw.text((text_x, curr_y + 2), name_str, fill=text_color, font=font_name)
        handle_str = f"@{author_username}" if author_username else "@threads"
        draw.text((text_x, curr_y + 42), handle_str, fill=subtext_color, font=font_handle)

        # Badge: "BÀI GỐC", "BÌNH LUẬN", or "MỞ ĐẦU"
        if card_type == "hook":
            badge_text = "⚡ MỞ ĐẦU"
            badge_bg = (133, 77, 14, 255)
            badge_outline = (234, 179, 8, 255)
            badge_text_color = (254, 240, 138, 255)
        elif card_type == "post":
            badge_text = "BÀI GỐC"
            badge_bg = (39, 39, 42, 255)
            badge_outline = (82, 82, 91, 255)
            badge_text_color = (212, 212, 216, 255)
        else:
            badge_text = "BÌNH LUẬN"
            badge_bg = (39, 39, 42, 255)
            badge_outline = (82, 82, 91, 255)
            badge_text_color = (212, 212, 216, 255)

        bbox_b = draw.textbbox((0, 0), badge_text, font=font_badge)
        bw = bbox_b[2] - bbox_b[0]
        badge_x = card_width - padding_x - bw - 24
        draw.rounded_rectangle(
            [(badge_x, curr_y + 10), (card_width - padding_x, curr_y + 46)],
            radius=12,
            fill=badge_bg,
            outline=badge_outline,
            width=1
        )
        draw.text((badge_x + 12, curr_y + 17), badge_text, fill=badge_text_color, font=font_badge)

        curr_y += header_height + 20

        # 2. Content
        for line in lines:
            draw.text((padding_x, curr_y), line, fill=text_color, font=font_content)
            curr_y += line_height

        curr_y += 20

        # 3. Footer (Likes & Replies metadata)
        like_text = f"❤️ {like_count:,}" if like_count is not None else "❤️ Thích"
        reply_text = f"💬 {reply_count:,}" if reply_count is not None else "💬 Phản hồi"
        draw.text((padding_x, curr_y), f"{like_text}    {reply_text}", fill=subtext_color, font=font_footer)

        # Save PNG with alpha transparency
        img.save(str(output_path), "PNG")
        return output_path

card_generator = CardGenerator()
