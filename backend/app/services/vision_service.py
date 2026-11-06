"""Crop photo analysis through Groq's Qwen vision model."""
import base64
import logging

from app.config import GROQ_VISION_MODEL, SUPPORTED_LANGUAGES
from app.services import llm_service

log = logging.getLogger("vision")


def sniff_mime(data: bytes):
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def analyze_crop_image(image: bytes, mime: str, language: str, note: str = ""):
    if llm_service.client is None:
        raise RuntimeError("GROQ_API_KEY is missing; image analysis is unavailable.")
    if not image or mime not in {"image/jpeg", "image/png", "image/webp"}:
        raise ValueError("Please upload a valid JPG, PNG or WEBP crop photo.")
    lang = SUPPORTED_LANGUAGES.get(language)
    if not lang:
        raise ValueError("Unsupported language for crop image analysis.")

    data_url = f"data:{mime};base64,{base64.b64encode(image).decode('ascii')}"
    prompt = f"""You are a cautious crop-health assistant for Indian farmers. Respond only in {lang}, using simple language and short sentences.

Farmer context (may be incomplete): {note or 'Not provided'}

Inspect the attached crop photograph. First describe only visible observations (crop/plant if identifiable, leaf colour, spots, holes, wilting, insects or other visible signs). Then state up to two possible explanations, explicitly saying they are possibilities and not a confirmed diagnosis. Give only low-risk immediate steps such as taking a clearer close-up photo, checking nearby plants and avoiding unnecessary spraying. Do not prescribe pesticide or fungicide names, doses, mixtures or schedules. Do not invent a diagnosis if the image is unclear. Ask one useful follow-up question if crop name or growth stage is needed. Recommend confirmation by a local KVK or agriculture officer before chemical treatment. Keep the answer under 120 words. Do not claim that the photo proves a disease."""

    try:
        response = llm_service.client.chat.completions.create(
            model=GROQ_VISION_MODEL,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]}],
            temperature=0.2,
            max_completion_tokens=900,
        )
        answer = (response.choices[0].message.content or "").strip()
        if not answer:
            raise RuntimeError("The vision model returned an empty answer. Please try a clearer photo.")
        return llm_service.clean_for_speech(answer)
    except Exception as exc:
        log.exception("Groq crop image analysis failed (model=%s)", GROQ_VISION_MODEL)
        raise RuntimeError(f"Crop image analysis service failed: {exc}") from exc
