from pathlib import Path
from PIL import Image
from backend.app.services.card_renderer.card_generator import card_generator

def test_card_generator_creates_valid_png(tmp_path):
    out_png = tmp_path / "test_render.png"
    card_generator.create_card(
        author_username="test_author",
        author_display_name="Tác giả Thử Nghiệm",
        content="Đây là một bình luận rất hay về công nghệ và làm video ngắn năm 2026!",
        output_path=out_png,
        card_type="comment",
        like_count=150,
        reply_count=8,
        theme="dark"
    )

    assert out_png.exists()
    assert out_png.stat().st_size > 1000

    # Verify PNG header and dimensions
    with Image.open(out_png) as img:
        assert img.format == "PNG"
        assert img.mode == "RGBA"
        assert img.width == 940
        assert img.height > 200
