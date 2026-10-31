import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.api.projects import router as projects_router
from backend.app.api.threads import router as threads_router
from backend.app.api.comments import router as comments_router
from backend.app.api.tts import router as tts_router
from backend.app.api.media import router as media_router
from backend.app.api.render import router as render_router
from backend.app.api.capcut import router as capcut_router
from backend.app.api.publishing import router as publishing_router
from backend.app.api.settings import router as settings_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("studio.main")

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Threads Comment Video Studio API",
    description="Chuyển đổi bài viết Threads thành video ngắn 9:16 có thuyết minh tiếng Việt và xuất dự án CapCut Desktop.",
    version="1.0.0"
)

# CORS middleware for local frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(projects_router, prefix="/api")
app.include_router(threads_router, prefix="/api")
app.include_router(comments_router, prefix="/api")
app.include_router(tts_router, prefix="/api")
app.include_router(media_router, prefix="/api")
app.include_router(render_router, prefix="/api")
app.include_router(capcut_router, prefix="/api")
app.include_router(publishing_router, prefix="/api")
app.include_router(settings_router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "Threads Comment Video Studio",
        "capcut_detected": bool(settings.CAPCUT_DRAFT_FOLDER),
        "capcut_folder": settings.CAPCUT_DRAFT_FOLDER,
        "ffmpeg_status": "ready"
    }

# Static mounting for frontend build MUST be after all API routes
frontend_dist = settings.BASE_DIR / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.STUDIO_HOST, port=settings.STUDIO_PORT, reload=settings.DEBUG)
