import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.config import SUPPORTED_LANGUAGES
from app.services.tts_service import generate_speech

log = logging.getLogger("tts")
router = APIRouter(prefix="/api/voice", tags=["Voice Assistant"])


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    language: str = "te-IN"


@router.post("/speak")
def speak(request: TTSRequest):
    if request.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(400, "Unsupported language.")
    try:
        audio = generate_speech(text=request.text, language=request.language)
        return Response(content=audio, media_type="audio/wav",
                        headers={"Content-Disposition": "inline; filename=rythuvoice.wav"})
    except Exception as e:
        log.error("TTS route error: %r", e)
        raise HTTPException(502, f"Speech generation failed: {e}")
