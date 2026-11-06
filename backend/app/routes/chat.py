from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app import db
from app.config import SUPPORTED_LANGUAGES
from app.services.ai_service import answer_question

router = APIRouter(prefix="/api/chat", tags=["AI Assistant"])


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    language: str = "te-IN"


@router.post("/ask")
def ask_question(request: ChatRequest, x_farmer_id: str | None = Header(None)):
    if request.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(400, f"Unsupported language. Use one of {list(SUPPORTED_LANGUAGES)}")
    try:
        answer, sources = answer_question(db.valid_farmer_id(x_farmer_id), request.question.strip(),
                                          request.language, kind="text")
    except Exception as e:
        raise HTTPException(502, str(e))
    return {"success": True, "question": request.question, "answer": answer,
            "language": request.language, "sources": sources}
