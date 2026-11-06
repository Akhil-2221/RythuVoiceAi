import os
import requests
from dotenv import load_dotenv

from pathlib import Path
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

PRISMA_API_URL = os.getenv("PRISMA_API_URL")
PRISMA_API_KEY = os.getenv("GNANI_API_KEY")

PRISMA_AUTH_HEADER = os.getenv(
    "PRISMA_AUTH_HEADER",
    "X-API-Key-ID"
)

PRISMA_AUDIO_FIELD = os.getenv(
    "PRISMA_AUDIO_FIELD",
    "audio_file"
)

PRISMA_LANGUAGE_FIELD = os.getenv(
    "PRISMA_LANGUAGE_FIELD",
    "language"
)


def transcribe_audio(audio_bytes: bytes, filename: str, language: str):
    if not PRISMA_API_URL or not PRISMA_API_KEY:
        raise ValueError("Prisma API configuration is missing.")

    headers = {
        PRISMA_AUTH_HEADER: PRISMA_API_KEY
    }

    files = {
        PRISMA_AUDIO_FIELD: (
            filename,
            audio_bytes,
            "audio/wav"
        )
    }

    data = {
    "language_code": language,
    "preferred_language": language,
    "format": "transcribe",
    "itn_native_numerals": "true"
}
    response = requests.post(
        PRISMA_API_URL,
        headers=headers,
        files=files,
        data=data,
        timeout=60
    )

    if not response.ok:
        print("GNANI STT STATUS:", response.status_code)
        print("GNANI STT RESPONSE:", response.text[:2000])
        print("GNANI STT HEADERS:", dict(response.headers))

    response.raise_for_status()

    return response.json()