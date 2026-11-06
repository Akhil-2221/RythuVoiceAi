"""Agricultural RAG: PDF ingestion -> chunking -> embeddings -> SQLite vector store -> retrieval.

Embedding backends (EMBEDDING_BACKEND):
  * sentence-transformers : real multilingual semantic embeddings (default model
    intfloat/multilingual-e5-small, ~118M params, fine for a 16 GB laptop).
    Set EMBEDDING_MODEL=google/embeddinggemma-300m to use EmbeddingGemma (needs HF access/token).
  * lexical : keyword TF-IDF fallback. NOT multilingual-semantic; use only when no model is installed.
No documents are bundled. Put real ICAR/SAU/KVK/government PDFs in backend/knowledge/ and run scripts/ingest.py.
"""
import json
import logging
import math
import re
from collections import Counter
from pathlib import Path
import os
from groq import Groq

import numpy as np

from app import db
from app.config import EMBEDDING_BACKEND, EMBEDDING_MODEL, KNOWLEDGE_DIR, RAG_MIN_SCORE, RAG_TOP_K

log = logging.getLogger("rag")
_model = None

_cache = {
    "n": -1,
    "rows": None,
    "mat": None
}
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

query_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
print("RAG Groq client initialized:", query_client is not None)
print("RAG Groq model:", GROQ_MODEL)
_cache = {"n": -1, "rows": None, "mat": None}


def _tok(text):
    return re.findall(r"\w+", text.lower())


# ---------------- embeddings ----------------
def _load_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer  # optional dependency
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _is_gemma():
    return "embeddinggemma" in EMBEDDING_MODEL.lower()


def embed_documents(texts):
    m = _load_model()
    if _is_gemma():
        v = m.encode_document(texts, normalize_embeddings=True)
    elif "e5" in EMBEDDING_MODEL.lower():
        v = m.encode([f"passage: {t}" for t in texts], normalize_embeddings=True)
    else:
        v = m.encode(texts, normalize_embeddings=True)
    return np.asarray(v, dtype=np.float32)


def embed_query(text):
    m = _load_model()
    if _is_gemma():
        v = m.encode_query([text], normalize_embeddings=True)
    elif "e5" in EMBEDDING_MODEL.lower():
        v = m.encode([f"query: {text}"], normalize_embeddings=True)
    else:
        v = m.encode([text], normalize_embeddings=True)
    return np.asarray(v, dtype=np.float32)[0]


# ---------------- ingestion ----------------
def chunk_text(text, size=900, overlap=150):
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 1 <= size:
            cur = f"{cur}\n{p}".strip()
            continue
        if cur:
            chunks.append(cur)
        while len(p) > size:
            chunks.append(p[:size])
            p = p[size - overlap:]
        cur = (cur[-overlap:] + "\n" + p).strip() if cur and len(p) < size else p
    if cur:
        chunks.append(cur)
    return [c for c in chunks if len(c) > 60]


def extract_pdf_pages(path):
    from pypdf import PdfReader
    out = []
    for i, page in enumerate(PdfReader(str(path)).pages, start=1):
        t = (page.extract_text() or "").strip()
        if t:
            out.append((i, t))
    return out


def ingest_directory(directory=KNOWLEDGE_DIR):
    directory = Path(directory)
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text("utf-8")) if manifest_path.exists() else {}
    pdfs = sorted(directory.glob("*.pdf"))
    if not pdfs:
        return {"documents": 0, "chunks": 0, "note": f"No PDFs found in {directory}. Add real source documents first."}
    db.init_db()
    use_embed = EMBEDDING_BACKEND == "sentence-transformers"
    total = 0
    for pdf in pdfs:
        meta = manifest.get(pdf.name, {})
        pieces = [(pg, c) for pg, t in extract_pdf_pages(pdf) for c in chunk_text(t)]
        if not pieces:
            log.warning("No extractable text in %s (scanned? needs OCR)", pdf.name)
            continue
        embs = embed_documents([c for _, c in pieces]) if use_embed else [None] * len(pieces)
        with db.conn() as c:
            c.execute("DELETE FROM chunks WHERE source=?", (pdf.name,))
            for (pg, text), e in zip(pieces, embs):
                c.execute("INSERT INTO chunks(source,title,publisher,url,page,text,embedding) VALUES(?,?,?,?,?,?,?)",
                          (pdf.name, meta.get("title", pdf.stem), meta.get("publisher"), meta.get("url"), pg, text,
                           e.tobytes() if e is not None else None))
        total += len(pieces)
    _cache["n"] = -1
    return {"documents": len(pdfs), "chunks": total, "backend": EMBEDDING_BACKEND}
def translate_search_query(query):
    """Translate Telugu/Hindi agricultural questions into English search queries."""

    if not query_client:
        return query

    try:
        response = query_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a translation engine. "
                        "Translate the user's question into English. "
                        "The output MUST be in English, never Telugu or Hindi. "
                        "Preserve all crop names and agricultural meaning. "
                        "Example: వరి means rice or paddy. "
                        "Return only the English translation."
                    )
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=0,
            max_tokens=300
        )

        translated = (
            response.choices[0].message.content or ""
        ).strip()

        if not translated:
            return query

        # Reject output that still contains Telugu or Devanagari characters.
        if re.search(r"[\u0C00-\u0C7F\u0900-\u097F]", translated):
            log.warning("Translation was not in English: %s", translated)
            return query

        return translated

    except Exception:
        log.exception("Agricultural query translation failed")
        return query

# ---------------- retrieval ----------------
def _load_rows():
    with db.conn() as c:
        n = c.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        if n != _cache["n"]:
            rows = [dict(r) for r in c.execute("SELECT * FROM chunks")]
            _cache.update(n=n, rows=rows, mat=None)
            if rows and rows[0]["embedding"]:
                _cache["mat"] = np.vstack([np.frombuffer(r["embedding"], dtype=np.float32) for r in rows])
    return _cache["rows"] or []


def status():
    rows = _load_rows()
    return {"backend": EMBEDDING_BACKEND, "model": EMBEDDING_MODEL if EMBEDDING_BACKEND != "lexical" else None,
            "chunks": len(rows), "documents": len({r["source"] for r in rows}),
            "ready": bool(rows),
            "warning": None if rows else "Knowledge base is empty: add PDFs to backend/knowledge and run scripts/ingest.py."}


def retrieve(query, k=RAG_TOP_K):
    """
    Multilingual hybrid-query retrieval.

    Searches using:
    1. Original Telugu/Hindi question.
    2. English-enhanced agricultural search query.

    Combines results and removes duplicate passages.
    """
    rows = _load_rows()

    if not rows:
        return []

    # Generate English search query
    english_query = translate_search_query(query)

    queries = [query]

    if english_query and english_query.lower() != query.lower():
        queries.append(english_query)

    combined_scores = np.zeros(len(rows), dtype=np.float32)

    for search_query in queries:

        if (
            _cache["mat"] is not None
            and EMBEDDING_BACKEND == "sentence-transformers"
        ):
            scores = _cache["mat"] @ embed_query(search_query)

        else:
            q = Counter(_tok(search_query))
            df = Counter()
            toks = [Counter(_tok(r["text"])) for r in rows]

            for t in toks:
                df.update(t.keys())

            N = len(rows)

            scores = np.array([
                sum(
                    (t[w] / (1 + len(t) ** 0.5))
                    * math.log(1 + N / (1 + df[w]))
                    for w in q if w in t
                )
                for t in toks
            ], dtype=np.float32)

            if scores.max() > 0:
                scores = scores / scores.max() * 0.9

        # Keep the strongest score for each document chunk
        combined_scores = np.maximum(combined_scores, scores)

    # Select highest scoring chunks
    order = np.argsort(-combined_scores)

    results = []

    for i in order:
        score = float(combined_scores[i])

        if score < RAG_MIN_SCORE:
            continue

        r = rows[i]

        results.append({
            "source": r["source"],
            "title": r["title"],
            "publisher": r["publisher"],
            "url": r["url"],
            "page": r["page"],
            "text": r["text"],
            "score": round(score, 3)
        })

        if len(results) >= k:
            break

    log.info(
        "RAG retrieved %d chunks using %d search queries",
        len(results),
        len(queries)
    )

    return results
