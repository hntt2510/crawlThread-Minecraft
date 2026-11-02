import pytest
from pathlib import Path
from backend.app.services.sfx.sfx_manager import sfx_manager
from backend.app.services.gameplay.gameplay_manager import gameplay_manager

def test_sfx_manager_provides_valid_wav_files():
    sfx_items = sfx_manager.get_available_sfx()
    assert len(sfx_items) >= 5
    ids = [it.id for it in sfx_items]
    assert "whoosh" in ids
    assert "punchline" in ids
    assert "pop" in ids

    # Check physical file exists and is readable
    whoosh_path = sfx_manager.get_sfx_path("whoosh")
    assert whoosh_path is not None
    assert whoosh_path.exists()
    assert whoosh_path.stat().st_size > 100

def test_gameplay_manager_catalog_and_segment_selection():
    clips = gameplay_manager.list_gameplay_clips()
    assert len(clips) >= 1
    
    seg = gameplay_manager.select_smart_segment(required_duration_sec=15.0)
    assert seg["file_path"].exists()
    assert seg["duration_sec"] > 0
    assert seg["start_time_sec"] >= 0.0
