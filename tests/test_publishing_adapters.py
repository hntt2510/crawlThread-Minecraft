import pytest
from pathlib import Path
from backend.app.services.publishing.publishing_service import publishing_service

def test_publishing_service_validation(tmp_path):
    dummy_video = tmp_path / "dummy.mp4"
    dummy_video.write_bytes(b"\x00\x00\x00\x20ftypisom" + b"\x00" * 2000)

    # Missing YouTube token should raise ValueError
    with pytest.raises(ValueError, match="YouTube Access Token"):
        publishing_service.publish_to_platforms(
            video_path=dummy_video,
            platforms=["youtube"],
            youtube_meta={},
            facebook_meta={},
            tiktok_meta={}
        )

    # Missing Facebook Page ID/token should raise ValueError
    with pytest.raises(ValueError, match="Facebook Page ID"):
        publishing_service.publish_to_platforms(
            video_path=dummy_video,
            platforms=["facebook"],
            youtube_meta={},
            facebook_meta={},
            tiktok_meta={}
        )

    # Missing TikTok token should raise ValueError
    with pytest.raises(ValueError, match="TikTok Access Token"):
        publishing_service.publish_to_platforms(
            video_path=dummy_video,
            platforms=["tiktok"],
            youtube_meta={},
            facebook_meta={},
            tiktok_meta={}
        )
