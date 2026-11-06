"""MOCKED tests: external APIs (Gnani STT/TTS, Groq) are replaced with fakes.
They verify our own logic (validation, limits, history, RAG, rate limiting) - NOT the live vendors."""
import base64, os, sys, tempfile
os.environ["DATABASE_PATH"] = os.path.join(tempfile.mkdtemp(), "t.db")
os.environ["RATE_LIMIT_PER_MIN"] = "1000"
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes import voice
from app.services import ai_service, rag_service, llm_service
from app import db

FID = "farmer_test_12345"
WAV = b"RIFF" + b"\x00" * 2000


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(voice, "transcribe_audio", lambda *a, **k: {"transcript": "పత్తి ఆకులు పసుపు రంగులోకి మారాయి"})
    monkeypatch.setattr(voice, "generate_speech", lambda t, l: b"FAKEWAV")
    monkeypatch.setattr(ai_service, "generate_llm_response", lambda q, l, history=None, chunks=None: "Answer [S1]" if chunks else "Answer")
    with TestClient(app) as c:
        yield c


def post_voice(c, lang="te-IN", data=WAV, fid=FID):
    return c.post("/api/voice/conversation", files={"audio": ("a.wav", data, "audio/wav")},
                  data={"language": lang}, headers={"X-Farmer-Id": fid})


def test_health(client):
    assert client.get("/health").json()["status"] == "healthy"


@pytest.mark.parametrize("lang", ["te-IN", "hi-IN", "en-IN"])
def test_voice_pipeline_languages(client, lang):
    r = post_voice(client, lang)
    assert r.status_code == 200
    j = r.json()
    assert j["farmer_question"] and j["ai_response"] == "Answer"
    assert base64.b64decode(j["audio_base64"]) == b"FAKEWAV"


def test_validation(client):
    assert post_voice(client, "xx-XX").status_code == 400
    assert post_voice(client, data=b"").status_code == 400
    assert post_voice(client, data=b"x" * (11 * 1024 * 1024)).status_code == 413


def test_tts_failure_still_returns_text(client, monkeypatch):
    def boom(t, l): raise RuntimeError("tts down")
    monkeypatch.setattr(voice, "generate_speech", boom)
    j = post_voice(client).json()
    assert j["audio_base64"] is None and j["tts_error"] and j["ai_response"]


def test_history_and_prefs(client):
    post_voice(client)
    h = client.get("/api/history", headers={"X-Farmer-Id": FID}).json()["messages"]
    assert len(h) >= 1 and h[-1]["language"] == "te-IN"
    client.put("/api/preferences", json={"language": "hi-IN", "autoplay": False}, headers={"X-Farmer-Id": FID})
    assert client.get("/api/preferences", headers={"X-Farmer-Id": FID}).json() == {"language": "hi-IN", "autoplay": False}
    assert client.get("/api/history").status_code == 400
    assert client.delete("/api/history", headers={"X-Farmer-Id": FID}).json()["deleted"] >= 1


def test_rag_lexical_retrieval_and_citation(client, monkeypatch):
    # synthetic TEST chunk inserted directly (not a real agricultural document)
    with db.conn() as c:
        c.execute("INSERT INTO chunks(source,title,page,text) VALUES('test.pdf','TEST DOC',3,?)",
                  ("Yellowing of cotton leaves can be caused by nitrogen deficiency or sucking pests like whitefly. " * 3,))
    rag_service._cache["n"] = -1
    hits = rag_service.retrieve("cotton leaves yellow whitefly")
    assert hits and hits[0]["source"] == "test.pdf"
    r = client.post("/api/chat/ask", json={"question": "cotton leaves yellow whitefly", "language": "en-IN"},
                    headers={"X-Farmer-Id": FID})
    assert r.json()["sources"][0]["title"] == "TEST DOC"
    assert "[S1]" not in r.json()["answer"]


def test_clean_for_speech():
    assert llm_service.clean_for_speech("**Hi** [S1] there #") == "Hi there"


def test_vision_rejects_non_image(client):
    r = client.post("/api/vision/analyze", files={"image": ("x.png", b"notanimage", "image/png")}, data={"language": "en-IN"})
    assert r.status_code == 415


def test_rate_limit():
    from app.middleware import RateLimitMiddleware
    from fastapi import FastAPI
    a = FastAPI(); a.add_middleware(RateLimitMiddleware, per_minute=2)
    @a.get("/api/x")
    def x(): return 1
    c = TestClient(a)
    assert [c.get("/api/x").status_code for _ in range(3)] == [200, 200, 429]
