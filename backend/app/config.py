"""Central configuration. All secrets come from environment variables / backend/.env."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


def _int(name, default):
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


def _list(name, default):
    return [x.strip() for x in os.getenv(name, default).split(",") if x.strip()]


SUPPORTED_LANGUAGES = {"te-IN": "Telugu", "hi-IN": "Hindi", "en-IN": "English"}

ENV = os.getenv("APP_ENV", "development")
CORS_ORIGINS = _list("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
MAX_AUDIO_MB = _int("MAX_AUDIO_MB", 10)
MAX_IMAGE_MB = _int("MAX_IMAGE_MB", 5)
RATE_LIMIT_PER_MIN = _int("RATE_LIMIT_PER_MIN", 30)
GROQ_TIMEOUT_S = _int("GROQ_TIMEOUT_S", 40)
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "rythuvoice.db"))
_configured_vision_model = os.getenv("GROQ_VISION_MODEL", "").strip()
# Replace the old Llama 4 Scout default from earlier project versions with
# Groq's currently documented Qwen vision model. Other explicit overrides remain supported.
GROQ_VISION_MODEL = (
    "qwen/qwen3.8-27b"
    if not _configured_vision_model or _configured_vision_model == "meta-llama/llama-4-scout-17b-16e-instruct"
    else _configured_vision_model
)
EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "lexical")  # lexical | sentence-transformers
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
RAG_TOP_K = _int("RAG_TOP_K", 4)
RAG_MIN_SCORE = float(os.getenv("RAG_MIN_SCORE", "0.30"))
KNOWLEDGE_DIR = Path(os.getenv("KNOWLEDGE_DIR", str(BASE_DIR / "knowledge")))
