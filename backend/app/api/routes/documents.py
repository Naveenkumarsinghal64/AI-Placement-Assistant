import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import DOCUMENT_UPLOADS_DIR
from app.models.schemas import DocumentInfo
from app.services import rag_service

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.get("", response_model=list[DocumentInfo])
def get_documents():
    return rag_service.list_documents()


@router.post("", response_model=DocumentInfo, status_code=201)
def upload_document(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    destination = DOCUMENT_UPLOADS_DIR / f"{uuid.uuid4()}{suffix}"
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = rag_service.ingest_document(destination, file.filename)
        return DocumentInfo(**result)
    except ValueError as exc:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: str):
    deleted = rag_service.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
