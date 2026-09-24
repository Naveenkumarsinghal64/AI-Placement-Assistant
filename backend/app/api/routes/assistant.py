from fastapi import APIRouter, HTTPException

from app.models.schemas import AssistantQuery, AssistantResponse
from app.services import rag_service

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/ask", response_model=AssistantResponse)
def ask_assistant(payload: AssistantQuery):
    try:
        result = rag_service.answer_question(payload.question)
        return AssistantResponse(**result)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
