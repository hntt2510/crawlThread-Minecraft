import json
import zipfile
from pathlib import Path
from backend.app.services.card_renderer.card_generator import card_generator
from backend.app.services.video_composer.ffmpeg_composer import VideoScene
from backend.app.services.capcut_exporter.builder import capcut_exporter

def test_capcut_exporter_structure(tmp_path):
    card1 = tmp_path / "card1.png"
    card2 = tmp_path / "card2.png"
    card_generator.create_card("user1", "User One", "Bài viết gốc số 1", card1, "post")
    card_generator.create_card("user2", "User Two", "Bình luận số 2", card2, "comment")

    scenes = [
        VideoScene(card_image_path=card1, duration_sec=3.0),
        VideoScene(card_image_path=card2, duration_sec=4.0)
    ]

    export_result = capcut_exporter.export_project(
        project_name="Capcut_Test_Project",
        scenes=scenes,
        install_to_local=False,
        output_dir=tmp_path / "exports"
    )

    assert export_result.draft_dir.exists()
    content_json_path = export_result.draft_dir / "draft_content.json"
    meta_json_path = export_result.draft_dir / "draft_meta_info.json"

    assert content_json_path.exists()
    assert meta_json_path.exists()

    content_data = json.loads(content_json_path.read_text(encoding="utf-8"))
    assert "tracks" in content_data
    assert len(content_data["tracks"]) >= 2  # V1, V2, V3 etc.
    assert content_data["duration"] == 7_000_000  # 7 seconds in microseconds

    # Verify portable package ZIP
    assert export_result.package_zip_path is not None
    assert export_result.package_zip_path.exists()
    with zipfile.ZipFile(export_result.package_zip_path, "r") as z:
        names = z.namelist()
        assert any("draft_content.json" in n for n in names)
        assert any("HUONG_DAN_IMPORT.txt" in n for n in names)
        assert any("capcut_import.py" in n for n in names)
