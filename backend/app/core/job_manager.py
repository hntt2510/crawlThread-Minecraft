import uuid
import threading
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger("studio.job_manager")

class Job:
    def __init__(self, job_id: str, job_type: str, project_id: Optional[str] = None):
        self.id = job_id
        self.type = job_type
        self.project_id = project_id
        self.status = "pending"  # pending, running, completed, failed
        self.progress = 0  # 0 to 100
        self.message = "Đang khởi tạo..."
        self.error: Optional[str] = None
        self.result: Optional[Dict[str, Any]] = None
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def update(self, progress: int, message: str, status: Optional[str] = None):
        self.progress = max(0, min(100, progress))
        self.message = message
        if status:
            self.status = status
        self.updated_at = datetime.now(timezone.utc)
        logger.info(f"[Job {self.id}] {self.progress}% - {self.message}")

    def complete(self, result: Dict[str, Any]):
        self.progress = 100
        self.status = "completed"
        self.message = "Hoàn thành"
        self.result = result
        self.updated_at = datetime.now(timezone.utc)
        logger.info(f"[Job {self.id}] Completed successfully")

    def fail(self, error_message: str):
        self.status = "failed"
        self.error = error_message
        self.message = f"Thất bại: {error_message}"
        self.updated_at = datetime.now(timezone.utc)
        logger.error(f"[Job {self.id}] Failed: {error_message}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "project_id": self.project_id,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "error": self.error,
            "result": self.result,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class JobManager:
    def __init__(self):
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()

    def create_job(self, job_type: str, project_id: Optional[str] = None) -> Job:
        job_id = str(uuid.uuid4())
        job = Job(job_id=job_id, job_type=job_type, project_id=project_id)
        with self._lock:
            self._jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)

    def run_in_background(self, job: Job, target_fn: Callable[..., Any], *args, **kwargs):
        def runner():
            job.update(5, "Đang bắt đầu xử lý...", status="running")
            try:
                result = target_fn(job, *args, **kwargs)
                job.complete(result or {})
            except Exception as e:
                logger.exception(f"Unhandled error in job {job.id}")
                job.fail(str(e))

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()

job_manager = JobManager()
