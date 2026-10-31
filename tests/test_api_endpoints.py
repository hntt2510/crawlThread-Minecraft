import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["ffmpeg_status"] == "ready"

def test_project_crud():
    # 1. Create
    create_res = client.post("/api/projects", json={
        "title": "API Test Project",
        "threads_url": "https://www.threads.net/@zuck/post/DeZgeQhm6RW"
    })
    assert create_res.status_code == 200
    proj_data = create_res.json()
    proj_id = proj_data["id"]
    assert proj_data["title"] == "API Test Project"

    # 2. Get
    get_res = client.get(f"/api/projects/{proj_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == proj_id

    # 3. Update
    patch_res = client.patch(f"/api/projects/{proj_id}", json={
        "title": "Updated API Project Title"
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Updated API Project Title"

    # 4. Delete
    del_res = client.delete(f"/api/projects/{proj_id}")
    assert del_res.status_code == 200

def test_tts_voices_endpoint():
    res = client.get("/api/tts/voices")
    assert res.status_code == 200
    voices = res.json()
    assert len(voices) >= 2
