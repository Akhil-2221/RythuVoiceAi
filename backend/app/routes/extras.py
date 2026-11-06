"""History, preferences, RAG status, crop image analysis, weather."""
import logging

from fastapi import APIRouter, UploadFile, File, Form, Header, HTTPException, Query
from pydantic import BaseModel

from app import db
from app.config import MAX_IMAGE_MB, SUPPORTED_LANGUAGES
from app.services import rag_service, vision_service, weather_service

log = logging.getLogger("extras")
router = APIRouter(prefix="/api", tags=["Extras"])


def _fid(x_farmer_id):
    fid = db.valid_farmer_id(x_farmer_id)
    if not fid:
        raise HTTPException(400, "Missing or invalid X-Farmer-Id header.")
    return fid


@router.get("/history")
def history(limit: int = Query(50, ge=1, le=200), x_farmer_id: str | None = Header(None)):
    return {"messages": db.list_messages(_fid(x_farmer_id), limit)}


@router.delete("/history")
def clear_history(x_farmer_id: str | None = Header(None)):
    return {"deleted": db.delete_messages(_fid(x_farmer_id))}


class Prefs(BaseModel):
    language: str = "te-IN"
    autoplay: bool = True


@router.get("/preferences")
def get_prefs(x_farmer_id: str | None = Header(None)):
    return db.get_prefs(_fid(x_farmer_id))


@router.put("/preferences")
def put_prefs(p: Prefs, x_farmer_id: str | None = Header(None)):
    if p.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(400, "Unsupported language.")
    db.set_prefs(_fid(x_farmer_id), p.language, p.autoplay)
    return p


@router.get("/rag/status")
def rag_status():
    return rag_service.status()


@router.post("/vision/analyze")
async def analyze_image(image: UploadFile = File(...), language: str = Form("te-IN"), note: str = Form(""),
                        x_farmer_id: str | None = Header(None)):
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(400, "Unsupported language.")
    data = await image.read()
    if len(data) > MAX_IMAGE_MB * 1024 * 1024:
        raise HTTPException(413, f"Image too large (max {MAX_IMAGE_MB} MB).")
    mime = vision_service.sniff_mime(data)
    if not mime:
        raise HTTPException(415, "Only JPEG, PNG or WEBP images are supported.")
    try:
        analysis = vision_service.analyze_crop_image(data, mime, language, note[:300])
    except Exception as e:
        log.error("Vision failed: %r", e)
        raise HTTPException(502, f"Image analysis failed: {e}")
    fid = db.valid_farmer_id(x_farmer_id)
    if fid:
        db.save_message(fid, language, "[crop photo]" + (f" {note[:200]}" if note else ""), analysis, [], "image")
    return {"success": True, "analysis": analysis, "language": language}


@router.get("/weather")
def weather(lat: float | None = None, lon: float | None = None, place: str | None = None):
    if (lat is None or lon is None) and not place:
        raise HTTPException(400, "Provide lat & lon, or place.")
    try:
        return weather_service.forecast(lat, lon, place)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(502, f"Weather service unavailable: {e}")
