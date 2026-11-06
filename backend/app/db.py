"""SQLite persistence: conversation history + farmer preferences (anonymous device id)."""
import json
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from app.config import DATABASE_PATH

_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def valid_farmer_id(value):
    return value if value and _ID_RE.match(value) else None


@contextmanager
def conn():
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DATABASE_PATH)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS messages(
          id INTEGER PRIMARY KEY AUTOINCREMENT, farmer_id TEXT NOT NULL,
          language TEXT NOT NULL, kind TEXT NOT NULL DEFAULT 'voice',
          question TEXT NOT NULL, answer TEXT NOT NULL, sources TEXT NOT NULL DEFAULT '[]',
          created_at TEXT NOT NULL DEFAULT (datetime('now')));
        CREATE INDEX IF NOT EXISTS idx_msg_farmer ON messages(farmer_id, id);
        CREATE TABLE IF NOT EXISTS preferences(
          farmer_id TEXT PRIMARY KEY, language TEXT NOT NULL DEFAULT 'te-IN',
          autoplay INTEGER NOT NULL DEFAULT 1, updated_at TEXT NOT NULL DEFAULT (datetime('now')));
        CREATE TABLE IF NOT EXISTS chunks(
          id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL, title TEXT,
          publisher TEXT, url TEXT, page INTEGER, text TEXT NOT NULL, embedding BLOB);
        """)


def save_message(farmer_id, language, question, answer, sources=None, kind="voice"):
    with conn() as c:
        cur = c.execute(
            "INSERT INTO messages(farmer_id,language,kind,question,answer,sources) VALUES(?,?,?,?,?,?)",
            (farmer_id, language, kind, question, answer, json.dumps(sources or [])))
        return cur.lastrowid


def list_messages(farmer_id, limit=50):
    with conn() as c:
        rows = c.execute("SELECT * FROM messages WHERE farmer_id=? ORDER BY id DESC LIMIT ?",
                         (farmer_id, limit)).fetchall()
    out = [dict(r, sources=json.loads(r["sources"])) for r in rows]
    return list(reversed(out))


def recent_context(farmer_id, n=4):
    return [(m["question"], m["answer"]) for m in list_messages(farmer_id, n)]


def delete_messages(farmer_id):
    with conn() as c:
        return c.execute("DELETE FROM messages WHERE farmer_id=?", (farmer_id,)).rowcount


def get_prefs(farmer_id):
    with conn() as c:
        r = c.execute("SELECT language,autoplay FROM preferences WHERE farmer_id=?", (farmer_id,)).fetchone()
    return {"language": r["language"], "autoplay": bool(r["autoplay"])} if r else {"language": "te-IN", "autoplay": True}


def set_prefs(farmer_id, language, autoplay):
    with conn() as c:
        c.execute("""INSERT INTO preferences(farmer_id,language,autoplay) VALUES(?,?,?)
          ON CONFLICT(farmer_id) DO UPDATE SET language=excluded.language,
          autoplay=excluded.autoplay, updated_at=datetime('now')""", (farmer_id, language, int(autoplay)))
