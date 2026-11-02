import json
import uuid
import time
import shutil
import zipfile
import logging
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
import pycapcut as cc

from backend.app.core.config import settings
from backend.app.services.video_composer.ffmpeg_composer import VideoScene

logger = logging.getLogger("studio.capcut_exporter")

class CapCutExportResult(BaseModel):
    draft_name: str
    draft_dir: Path
    installed_to_capcut: bool
    package_zip_path: Optional[Path] = None

class CapCutExporter:
    """Generates an editable native CapCut Desktop multi-track timeline project."""

    def export_project(
        self,
        project_name: str,
        scenes: List[VideoScene],
        background_video_path: Optional[Path] = None,
        background_music_path: Optional[Path] = None,
        background_music_volume: float = 0.2,
        install_to_local: bool = True,
        output_dir: Optional[Path] = None,
    ) -> CapCutExportResult:
        if not scenes:
            raise ValueError("Không có phân cảnh nào để tạo CapCut project.")

        # Sanitize project folder name
        safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in project_name).strip()
        if not safe_name:
            safe_name = f"Threads_Project_{int(time.time())}"

        # Target directory
        base_export_dir = output_dir or (settings.DATA_DIR / "capcut_exports" / safe_name)
        base_export_dir.mkdir(parents=True, exist_ok=True)
        staging_dir = base_export_dir / safe_name
        staging_dir.mkdir(parents=True, exist_ok=True)

        total_duration_sec = sum(s.duration_sec for s in scenes)
        total_duration_us = int(total_duration_sec * 1_000_000)

        # Initialize pycapcut DraftFolder
        draft_folder = cc.DraftFolder(str(base_export_dir))
        script = draft_folder.create_draft(safe_name, 1080, 1920, fps=30, allow_replace=True)

        # Assets subfolder to keep bundle fully self-contained (created after draft folder init)
        assets_bundle_dir = staging_dir / "project_assets"
        assets_bundle_dir.mkdir(parents=True, exist_ok=True)

        # Add distinct timeline tracks
        script.add_track(cc.TrackType.video, "V1_Background", absolute_index=0)
        script.add_track(cc.TrackType.video, "V0_Hook_Card", absolute_index=5)
        script.add_track(cc.TrackType.video, "V2_Post_Card", absolute_index=10)
        script.add_track(cc.TrackType.video, "V3_Comment_Cards", absolute_index=20)
        script.add_track(cc.TrackType.audio, "A1_Voiceovers", absolute_index=4)
        script.add_track(cc.TrackType.audio, "A3_Sound_Effects", absolute_index=8)
        if background_music_path and background_music_path.exists():
            script.add_track(cc.TrackType.audio, "A2_Background_Music", absolute_index=2)

        # 1. Add V1 Background Video
        if background_video_path and background_video_path.exists():
            bundled_bg = assets_bundle_dir / background_video_path.name
            if not bundled_bg.exists():
                shutil.copy2(background_video_path, bundled_bg)
            
            # Add video segment
            bg_trange = cc.Timerange(0, total_duration_us)
            bg_seg = cc.VideoSegment(str(bundled_bg), bg_trange)
            script.add_segment(bg_seg, "V1_Background")

        # 2. Add Cards & Audio clips per scene
        timeline_curr_us = 0
        for i, scene in enumerate(scenes):
            scene_dur_us = int(scene.duration_sec * 1_000_000)
            if getattr(scene, "is_hook", False):
                target_track = "V0_Hook_Card"
            elif i == 0 or (getattr(scenes[0], "is_hook", False) and i == 1):
                target_track = "V2_Post_Card"
            else:
                target_track = "V3_Comment_Cards"

            # Copy card image into bundle
            bundled_card = assets_bundle_dir / f"scene_{i:02d}_{scene.card_image_path.name}"
            if not bundled_card.exists():
                shutil.copy2(scene.card_image_path, bundled_card)

            card_trange = cc.Timerange(timeline_curr_us, scene_dur_us)
            card_seg = cc.VideoSegment(str(bundled_card), card_trange)
            script.add_segment(card_seg, target_track)

            # Add voice audio segment on A1
            if scene.audio_path and scene.audio_path.exists():
                bundled_audio = assets_bundle_dir / f"scene_{i:02d}_{scene.audio_path.name}"
                if not bundled_audio.exists():
                    shutil.copy2(scene.audio_path, bundled_audio)

                audio_trange = cc.Timerange(timeline_curr_us, scene_dur_us)
                audio_seg = cc.AudioSegment(str(bundled_audio), audio_trange, volume=1.0)
                script.add_segment(audio_seg, "A1_Voiceovers")

            # Add sound effect cues on A3
            for cue in getattr(scene, "sfx_cues", []):
                if cue.file_path and cue.file_path.exists():
                    bundled_sfx = assets_bundle_dir / f"sfx_{cue.sfx_id}_{cue.file_path.name}"
                    if not bundled_sfx.exists():
                        shutil.copy2(cue.file_path, bundled_sfx)
                    try:
                        audio_mat = cc.AudioMaterial(str(bundled_sfx))
                        sfx_dur_us = min(scene_dur_us, audio_mat.duration)
                        sfx_trange = cc.Timerange(timeline_curr_us, sfx_dur_us)
                        sfx_seg = cc.AudioSegment(audio_mat, sfx_trange, volume=cue.volume)
                        script.add_segment(sfx_seg, "A3_Sound_Effects")
                    except Exception as e:
                        logger.warning(f"Could not add SFX segment to CapCut: {e}")

            timeline_curr_us += scene_dur_us

        # 3. Add A2 Background Music
        if background_music_path and background_music_path.exists():
            bundled_music = assets_bundle_dir / background_music_path.name
            if not bundled_music.exists():
                shutil.copy2(background_music_path, bundled_music)
            
            music_trange = cc.Timerange(0, total_duration_us)
            music_seg = cc.AudioSegment(str(bundled_music), music_trange, volume=background_music_volume)
            script.add_segment(music_seg, "A2_Background_Music")

        # Save base draft
        script.save()

        # Patch CapCut Desktop metadata
        self._patch_metadata(staging_dir, safe_name, total_duration_us)

        installed_to_capcut = False
        # If CapCut Desktop folder exists and user requested local install, copy directly
        if install_to_local and settings.CAPCUT_DRAFT_FOLDER:
            capcut_dest = Path(settings.CAPCUT_DRAFT_FOLDER) / safe_name
            try:
                if capcut_dest.exists():
                    shutil.rmtree(capcut_dest)
                shutil.copytree(staging_dir, capcut_dest)
                # Patch metadata specifically for the CapCut local directory
                self._patch_metadata(capcut_dest, safe_name, total_duration_us)
                installed_to_capcut = True
                logger.info(f"Successfully installed draft to CapCut Desktop: {capcut_dest}")
            except Exception as e:
                logger.warning(f"Could not install to CapCut folder: {e}")

        # Package as standalone ZIP for easy sharing / download
        zip_path = base_export_dir / f"{safe_name}_CapCut_Package.zip"
        self._create_portable_package(staging_dir, zip_path, safe_name)

        return CapCutExportResult(
            draft_name=safe_name,
            draft_dir=staging_dir,
            installed_to_capcut=installed_to_capcut,
            package_zip_path=zip_path
        )

    def _patch_metadata(self, draft_path: Path, project_name: str, duration_us: int) -> None:
        """Patch draft_content.json and draft_meta_info.json for CapCut Desktop Windows compatibility."""
        draft_uuid = str(uuid.uuid4()).upper()
        now_ts = int(time.time())

        content_path = draft_path / "draft_content.json"
        if content_path.exists():
            content = json.loads(content_path.read_text(encoding="utf-8"))
            content["id"] = draft_uuid
            content["name"] = project_name
            content["duration"] = duration_us
            content["path"] = ""
            content["update_time"] = now_ts
            content["new_version"] = "179.0.0"
            content.setdefault("platform", {}).update({
                "os": "windows",
                "app_id": 359289,
                "app_source": "cc",
                "app_version": "6.7.0"
            })
            content_path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")

        meta_path = draft_path / "draft_meta_info.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        else:
            meta = {"draft_id": draft_uuid}
        meta["draft_name"] = project_name
        meta["draft_root_path"] = str(draft_path.parent).replace("\\", "/")
        meta["draft_fold_path"] = str(draft_path).replace("\\", "/")
        meta["tm_duration"] = duration_us
        meta["draft_new_version"] = "164.0.0"
        meta["draft_id"] = draft_uuid
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

        # Also update parent root_meta_info.json if present
        root_meta_path = draft_path.parent / "root_meta_info.json"
        if root_meta_path.exists():
            try:
                root_data = json.loads(root_meta_path.read_text(encoding="utf-8"))
                draft_store = root_data.setdefault("all_draft_store", [])
                # Remove previous entry for same draft_name if exists
                draft_store = [d for d in draft_store if d.get("draft_name") != project_name]
                draft_entry = {
                    "draft_id": draft_uuid,
                    "draft_name": project_name,
                    "draft_fold_path": str(draft_path).replace("\\", "/"),
                    "draft_root_path": str(draft_path.parent).replace("\\", "/"),
                    "draft_json_file": str(content_path).replace("\\", "/"),
                    "tm_draft_create": now_ts * 1000,
                    "tm_draft_modified": now_ts * 1000,
                    "tm_duration": duration_us,
                    "draft_new_version": "164.0.0"
                }
                draft_store.insert(0, draft_entry)
                root_data["all_draft_store"] = draft_store
                root_meta_path.write_text(json.dumps(root_data, ensure_ascii=False, indent=2), encoding="utf-8")
                logger.info("Successfully updated root_meta_info.json with draft entry")
            except Exception as e:
                logger.warning(f"Could not update root_meta_info.json: {e}")

    def _create_portable_package(self, draft_dir: Path, zip_path: Path, safe_name: str):
        """Create a complete handoff ZIP with import helper."""
        import_helper = f"""# CapCut Desktop Windows Import Helper
# Copy this folder to: %LOCALAPPDATA%\\CapCut\\User Data\\Projects\\com.lveditor.draft\\{safe_name}
# Or run this python script:
import os, shutil
from pathlib import Path
capcut_draft_root = Path(os.environ.get("LOCALAPPDATA", "")) / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft"
if not capcut_draft_root.exists():
    print("CapCut Desktop projects directory not found at:", capcut_draft_root)
else:
    dest = capcut_draft_root / "{safe_name}"
    src = Path(__file__).resolve().parent / "{safe_name}"
    if dest.exists(): shutil.rmtree(dest)
    shutil.copytree(src, dest)
    print("SUCCESS: Project imported to CapCut Desktop at:", dest)
"""
        (draft_dir.parent / "capcut_import.py").write_text(import_helper, encoding="utf-8")
        
        readme_text = f"""=== HUONG DAN IMPORT CAPCUT DESKTOP ===
1. Giải nén file zip này.
2. Sao chép toàn bộ thư mục '{safe_name}' vào đường dẫn:
   C:\\Users\\<Ten_Cua_Ban>\\AppData\\Local\\CapCut\\User Data\\Projects\\com.lveditor.draft\\
3. Mở CapCut Desktop, dự án '{safe_name}' sẽ xuất hiện ngay trong danh sách dự án gần đây với đầy đủ các track video, thẻ bình luận, âm thanh voiceover và nhạc nền!
"""
        (draft_dir.parent / "HUONG_DAN_IMPORT.txt").write_text(readme_text, encoding="utf-8")

        with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as z:
            for file_path in draft_dir.rglob("*"):
                arcname = file_path.relative_to(draft_dir.parent)
                z.write(file_path, arcname)
            z.write(draft_dir.parent / "capcut_import.py", "capcut_import.py")
            z.write(draft_dir.parent / "HUONG_DAN_IMPORT.txt", "HUONG_DAN_IMPORT.txt")

capcut_exporter = CapCutExporter()
