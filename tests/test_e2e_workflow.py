import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.services.card_renderer.card_generator import card_generator
from backend.app.services.video_composer.ffmpeg_composer import VideoScene
from backend.app.services.capcut_exporter.builder import capcut_exporter

client = TestClient(app)

def test_full_studio_workflow_integration(tmp_path):
    # 1. Create Project
    res = client.post("/api/projects", json={
        "title": "E2E Studio Project",
        "threads_url": "https://www.threads.net/@zuck/post/DeZgeQhm6RW"
    })
    assert res.status_code == 200
    proj_id = res.json()["id"]

    # 2. Check Voices
    v_res = client.get("/api/tts/voices")
    assert v_res.status_code == 200
    assert len(v_res.json()) >= 2

    # 3. Simulate selection update
    sel_res = client.post(f"/api/comments/project/{proj_id}/selections", json=[
        {
            "comment_id": "cmt_001",
            "sequence_order": 0,
            "display_text": "Bình luận hay số một",
            "tts_text": "Bình luận hay số một",
            "voice_id": "vi-VN-HoaiMyNeural",
            "voice_rate": 1.0,
            "is_active": True
        }
    ])
    assert sel_res.status_code == 200

    # 4. Generate Cards & CapCut project
    card_p = tmp_path / "card.png"
    card_generator.create_card("author", "Display Author", "Nội dung bài viết", card_p, "post")
    scenes = [VideoScene(card_image_path=card_p, duration_sec=3.0)]

    capcut_res = capcut_exporter.export_project(
        project_name="E2E_CapCut_Project",
        scenes=scenes,
        install_to_local=False,
        output_dir=tmp_path / "e2e_capcut"
    )
    assert capcut_res.draft_dir.exists()
    assert (capcut_res.draft_dir / "draft_content.json").exists()
    assert (capcut_res.draft_dir / "draft_meta_info.json").exists()
    assert capcut_res.package_zip_path.exists()
