from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.app.core.config import settings

router = APIRouter(prefix="/settings", tags=["settings"])

class AppSettingsSchema(BaseModel):
    capcut_draft_folder: str
    default_tts_provider: str
    fptai_api_key: Optional[str] = ""
    google_application_credentials: Optional[str] = ""
    youtube_client_id: Optional[str] = ""
    facebook_app_id: Optional[str] = ""
    tiktok_client_key: Optional[str] = ""

@router.get("", response_model=AppSettingsSchema)
def get_settings():
    return AppSettingsSchema(
        capcut_draft_folder=settings.CAPCUT_DRAFT_FOLDER,
        default_tts_provider=settings.DEFAULT_TTS_PROVIDER,
        fptai_api_key="***" if settings.FPTAI_API_KEY else "",
        google_application_credentials=settings.GOOGLE_APPLICATION_CREDENTIALS,
        youtube_client_id=settings.YOUTUBE_CLIENT_ID,
        facebook_app_id=settings.FACEBOOK_APP_ID,
        tiktok_client_key=settings.TIKTOK_CLIENT_KEY,
    )

@router.post("")
def update_settings(data: AppSettingsSchema):
    if data.capcut_draft_folder:
        settings.CAPCUT_DRAFT_FOLDER = data.capcut_draft_folder
    if data.fptai_api_key and data.fptai_api_key != "***":
        settings.FPTAI_API_KEY = data.fptai_api_key
    if data.google_application_credentials:
        settings.GOOGLE_APPLICATION_CREDENTIALS = data.google_application_credentials
    return {"success": True, "message": "Đã lưu cài đặt hệ thống thành công."}
