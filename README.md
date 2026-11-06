# RythuVoice AI

Voice-first multilingual (Telugu / Hindi / English) agricultural assistant.
**Farmer speech → Gnani Prisma STT → (RAG + history) → Groq LLM → Gnani Timbre TTS → spoken answer**

## Architecture
- `backend/` FastAPI. Existing Gnani/Groq integrations preserved (`prisma_service`, `tts_service`, `llm_service`); `/api/voice/conversation` request format unchanged (multipart `audio`, `language`), response extended with `sources`, `tts_error`.
- `frontend/` Next.js 14 + TypeScript + Tailwind (shadcn-style hand-written primitives; shadcn CLI not used). Browser records audio and converts to 16 kHz mono WAV client-side.
- SQLite (history, preferences, RAG chunks) keyed by an anonymous per-device ID (`X-Farmer-Id`). No login.

## Run locally
```bash
# backend
cd backend && python -m venv .venv && .venv\Scripts\activate   # (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt            # + install your working Gnani TTS SDK (gnani.tts)
copy .env.example .env  # keep your EXISTING .env if you have one
uvicorn app.main:app --reload --port 8000
# frontend
cd frontend && copy .env.example .env.local && npm install && npm run dev   # http://localhost:3000
```
Mobile testing: microphone needs HTTPS or localhost. Use Vercel preview/ngrok for a phone.

## RAG
1. Download REAL ICAR/ANGRAU/PJTSAU/KVK/government PDFs into `backend/knowledge/` (see its README; optional `manifest.json` for citation metadata).
2. `pip install -r requirements-rag.txt`, set `EMBEDDING_BACKEND=sentence-transformers` in `.env`.
3. `python -m scripts.ingest`; check `GET /api/rag/status`.
Default model `intfloat/multilingual-e5-small` (small, laptop-friendly, multilingual). For EmbeddingGemma set `EMBEDDING_MODEL=google/embeddinggemma-300m` (needs HF license acceptance + `HF_TOKEN`). The 63.5 GB Evon model is intentionally not used.
Until documents are ingested the assistant answers without citations and the prompt forbids exact doses/scheme details.

## Tests
`cd backend && pip install -r requirements-dev.txt && pytest tests` – **mocked** (fake STT/TTS/Groq). Live check: `python test_conversation.py` with real keys.

## Deploy
Backend: Docker (`backend/Dockerfile`) or `render.yaml`; set secrets in dashboard; set `CORS_ORIGINS` to the frontend URL. SQLite on free hosts is ephemeral - mount a persistent disk or move to Postgres for production history.
Frontend: Vercel, root `frontend`, env `NEXT_PUBLIC_API_BASE_URL=https://<backend>`.

## Status / limitations (honest)
- The submitted source includes mocked backend tests and a frontend production build script. In this packaging environment, dependency installation timed out, so a fresh `next build` and the full pytest suite could not be rerun here. Python syntax compilation passed for the modified backend modules, and the weather service passed a mocked forecast/geocoding check.
- Live external services still require verification with the owner's credentials and deployment network: Prisma STT, Groq chat/vision, Timbre TTS, Open-Meteo, and real-phone microphone/playback.
- Crop image analysis uses Groq Qwen vision (`qwen/qwen3.8-27b` by default). Weather uses Open-Meteo and supports GPS or manual Indian village/town search. Both require internet access; the vision model must be enabled for the Groq account.
- Four agricultural PDFs are included under `backend/knowledge/`. The SQLite database includes ingested RAG chunks; the scanned October 2026 Telugu magazine requires OCR before it can be searched.
- Rate limiter is in-memory (single instance). Scanned PDFs need OCR (not included).


## Submission checks for the three interactive features
- Language selector: Telugu, Hindi and English. English speech recognition/synthesis depends on the configured Prisma/Gnani account supporting `en-IN`; text chat and the AI response language support English in the application.
- Crop photo analysis: configure `GROQ_API_KEY` and `GROQ_VISION_MODEL=qwen/qwen3.8-27b` in `backend/.env`. The Groq account must have access to this vision model.
- Weather: no API key is needed. Allow browser location access on HTTPS/localhost, or enter an Indian village/town name manually. The backend must be able to reach Open-Meteo.
