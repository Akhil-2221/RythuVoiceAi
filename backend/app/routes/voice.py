import base64
import logging

from fastapi import APIRouter, UploadFile, File, Form, Header, HTTPException

from app import db
from app.config import MAX_AUDIO_MB, SUPPORTED_LANGUAGES
from app.services.ai_service import answer_question
from app.services.prisma_service import transcribe_audio
from app.services.tts_service import generate_speech

log = logging.getLogger("voice")
router = APIRouter(prefix="/api/voice", tags=["Voice Assistant"])


def extract_transcript(data):
    """Extract recognized text from Prisma's response."""
    if not isinstance(data, dict):
        return None
    if data.get("transcript"):
        return data["transcript"]
    output = data.get("output")
    if isinstance(output, dict) and output.get("literal"):
        return output["literal"]
    for value in data.values():
        if isinstance(value, dict):
            result = extract_transcript(value)
            if result:
                return result
    return None


def _check_language(language):
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(400, f"Unsupported language '{language}'. Use one of {list(SUPPORTED_LANGUAGES)}")


async def _read_audio(audio: UploadFile):
    data = await audio.read()
    if not data:
        raise HTTPException(400, "Uploaded audio file is empty.")
    if len(data) > MAX_AUDIO_MB * 1024 * 1024:
        raise HTTPException(413, f"Audio too large (max {MAX_AUDIO_MB} MB).")
    if len(data) < 1000:
        raise HTTPException(400, "Recording too short. Please speak again.")
    return data


@router.post("/transcribe")
async def transcribe(audio: UploadFile = File(...), language: str = Form("te-IN")):
    _check_language(language)
    data = await _read_audio(audio)
    try:
        result = transcribe_audio(data, audio.filename or "recording.wav", language)
    except Exception as e:
        log.error("STT failed: %r", e)
        raise HTTPException(502, f"Transcription failed: {e}")
    return {"success": True, "language": language, "transcription": result}


@router.post("/conversation")
async def voice_conversation(audio: UploadFile = File(...), language: str = Form("te-IN"),
                             x_farmer_id: str | None = Header(None)):
    _check_language(language)
    data = await _read_audio(audio)
    farmer_id = db.valid_farmer_id(x_farmer_id)
    try:
        stt = transcribe_audio(data, audio.filename or "recording.wav", language)   # 1. Prisma STT
    except Exception as e:
        log.error("STT failed: %r", e)
        raise HTTPException(502, f"Speech recognition failed: {e}")
    question = extract_transcript(stt)
    if not question or not question.strip():
        raise HTTPException(422, "Could not understand the speech. Please speak clearly and try again.")
    try:
        answer, sources = answer_question(farmer_id, question.strip(), language)   # 2. RAG + Groq
    except Exception as e:
        raise HTTPException(502, str(e))
    try:
        speech = generate_speech(answer, language)                                 # 3. Timbre TTS
        audio_b64 = base64.b64encode(speech).decode("utf-8")
        tts_error = None
    except Exception as e:  # text answer is still useful if TTS fails
        log.error("TTS failed: %r", e)
        audio_b64, tts_error = None, str(e)
    return {"success": True, "language": language, "farmer_question": question, "ai_response": answer,
            "sources": sources, "audio_base64": audio_b64, "audio_format": "wav", "tts_error": tts_error,
            "message": "Voice conversation completed successfully." if audio_b64 else "Answer ready; speech failed."}
