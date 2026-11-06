from app import db
from app.services import rag_service
from app.services.llm_service import generate_llm_response, clean_for_speech


def generate_response(question: str, language: str = "te-IN"):
    """Backward-compatible simple entry point (no history / RAG)."""
    return generate_llm_response(question, language)


def answer_question(farmer_id: str, question: str, language: str, kind: str = "voice"):
    """Full pipeline: history context + RAG retrieval + grounded Groq answer + persistence."""
    history = db.recent_context(farmer_id) if farmer_id else []
    try:
        chunks = rag_service.retrieve(question)
    except Exception:  # RAG must never break the voice flow
        chunks = []
    raw = generate_llm_response(question, language, history=history, chunks=chunks)
    used = [c for i, c in enumerate(chunks, 1) if f"[S{i}]" in raw]
    sources = [{"title": c["title"] or c["source"], "publisher": c["publisher"], "url": c["url"],
                "page": c["page"], "score": c["score"]} for c in used]
    answer = clean_for_speech(raw)
    if farmer_id:
        db.save_message(farmer_id, language, question, answer, sources, kind)
    return answer, sources
