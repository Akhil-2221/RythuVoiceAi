import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import db
from app.config import CORS_ORIGINS, ENV, RATE_LIMIT_PER_MIN
from app.middleware import RateLimitMiddleware
from app.routes.chat import router as chat_router
from app.routes.extras import router as extras_router
from app.routes.tts import router as tts_router
from app.routes.voice import router as voice_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_):
    db.init_db()
    yield


app = FastAPI(title="RythuVoice AI", description="Multilingual AI Voice Assistant for Indian Farmers",
              version="2.0.0", lifespan=lifespan,
              docs_url=None if ENV == "production" else "/docs", redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, per_minute=RATE_LIMIT_PER_MIN)

for r in (voice_router, chat_router, tts_router, extras_router):
    app.include_router(r)


@app.get("/")
def home():
    return {"message": "Welcome to RythuVoice AI!", "status": "Running"}


@app.get("/health")
def health():
    return {"status": "healthy", "application": "RythuVoice AI"}
