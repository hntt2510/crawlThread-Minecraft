import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.services.card_renderer.card_generator import card_generator
from backend.app.services.video_composer.ffmpeg_composer import VideoScene
from backend.app.services.capcut_exporter.builder import capcut_exporter

client = TestClient(app)

def test_full_studio_workflow_integration(tmp_path):
    # 1. Step 1A: Discovery Search
    disc_res = client.post("/api/discovery/search", json={
        "category": "lifestyle",
        "search_type": "BOTH",
        "media_type": "ALL",
        "time_window": "7d",
        "limit": 5
    })
    assert disc_res.status_code == 200
    disc_data = disc_res.json()["data"]
    assert len(disc_data["posts"]) > 0
    selected_post = disc_data["posts"][0]
    assert selected_post["threads_url"]

    # 2. Step 1B: Create Project from Selected Post
    res = client.post("/api/projects", json={
        "title": selected_post["content"][:40] or "E2E Studio Project",
        "threads_url": selected_post["threads_url"]
    })
    assert res.status_code == 200
    proj_id = res.json()["id"]

    # 3. Step 2: Comment Selections with Dual Text
    sel_res = client.post(f"/api/comments/project/{proj_id}/selections", json=[
        {
            "comment_id": "cmt_e2e_001",
            "sequence_order": 0,
            "display_text": "Bình luận hiển thị trên video",
            "tts_text": "Bình luận đọc thuyết minh bằng giọng nói AI",
            "voice_id": "vi-VN-HoaiMyNeural",
            "voice_rate": 1.0,
            "is_active": True
        }
    ])
    assert sel_res.status_code == 200

    # 4. Step 3: Check Vietnamese Voices
    v_res = client.get("/api/tts/voices")
    assert v_res.status_code == 200
    assert len(v_res.json()) >= 2
    assert any(v["id"] == "vi-VN-HoaiMyNeural" for v in v_res.json())

    # 5. Step 4: Card Generation & Scene Preparation
    card_p = tmp_path / "card.png"
    card_generator.create_card("author", "Display Author", "Nội dung bài viết", card_p, "post")
    scenes = [VideoScene(card_image_path=card_p, duration_sec=3.0)]

    # 6. Step 5: Multi-track CapCut Project Export
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

    # 7. Step 6: Publishing Validation (Security Confirmation Check)
    # Refuses publishing if confirm_publish is False
    unconfirmed_pub = client.post("/api/publishing/publish", json={
        "project_id": proj_id,
        "platforms": ["youtube"],
        "confirm_publish": False
    })
    assert unconfirmed_pub.status_code == 400
