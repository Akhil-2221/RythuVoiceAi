import logging
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")
log = logging.getLogger("tts")
_client = None


def _get_client():
    """Lazy init so the app (and tests) can start even before TTS credentials are set."""
    global _client
    if _client is None:
        api_key = os.getenv("PRISMA_API_KEY")
        if not api_key:
            raise ValueError("PRISMA_API_KEY is missing")
        from gnani.tts import GnaniTTSClient
        _client = GnaniTTSClient(api_key=api_key)
    return _client


def generate_speech(text: str, language: str = "te-IN"):
    log.info("TTS request language=%s chars=%d", language, len(text))
    audio = _get_client().synthesize(text, voice="Yukti", model="timbre-v2.5", language=language)
    log.info("TTS audio bytes=%d", len(audio))
    return audio
