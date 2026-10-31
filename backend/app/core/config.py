import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    STUDIO_HOST: str = "127.0.0.1"
    STUDIO_PORT: int = 8000
    DEBUG: bool = True
    
    # Storage
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    CACHE_DIR: Path = DATA_DIR / "cache"
    DATABASE_URL: str = f"sqlite:///{DATA_DIR / 'studio.db'}"
    
    # CapCut Windows Default
    CAPCUT_DRAFT_FOLDER: str = ""
    
    # TTS
    DEFAULT_TTS_PROVIDER: str = "edge_tts"
    FPTAI_API_KEY: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    
    # Publishing
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""
    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)
(settings.DATA_DIR / "projects").mkdir(parents=True, exist_ok=True)
(settings.DATA_DIR / "media").mkdir(parents=True, exist_ok=True)
(settings.CACHE_DIR / "audio").mkdir(parents=True, exist_ok=True)

# Detect CapCut folder if not provided or expand variables
if settings.CAPCUT_DRAFT_FOLDER:
    settings.CAPCUT_DRAFT_FOLDER = os.path.expandvars(settings.CAPCUT_DRAFT_FOLDER)
else:
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        default_cc = Path(local_app_data) / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft"
        if default_cc.exists():
            settings.CAPCUT_DRAFT_FOLDER = str(default_cc)
