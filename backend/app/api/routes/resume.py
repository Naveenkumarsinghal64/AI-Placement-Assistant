import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import RESUME_UPLOADS_DIR
from app.models.schemas import JobMatchResult, ResumeAnalysis
from app.services import resume_service

router = APIRouter(prefix="/api/resume", tags=["resume"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def _save_upload(upload: UploadFile) -> Path:
    suffix = Path(upload.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    destination = RESUME_UPLOADS_DIR / f"{uuid.uuid4()}{suffix}"
    with destination.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    return destination


@router.post("/analyze", response_model=ResumeAnalysis)
def analyze_resume(file: UploadFile = File(...)):
    file_path = _save_upload(file)
    try:
        result = resume_service.analyze_resume_file(file_path)
        return ResumeAnalysis(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        file_path.unlink(missing_ok=True)


@router.post("/match", response_model=JobMatchResult)
def match_job(file: UploadFile = File(...), job_description: str = Form(...)):
    file_path = _save_upload(file)
    try:
        result = resume_service.match_resume_to_job(file_path, job_description)
        return JobMatchResult(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        file_path.unlink(missing_ok=True)
