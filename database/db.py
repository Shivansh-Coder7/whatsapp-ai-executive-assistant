"""
SQLite storage layer. Three tables:
  conversations  -> every message pair, for history + admin search
  meetings       -> meeting requests captured by the scheduler
  users          -> lightweight per-number state (name, last_seen)
"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from config.settings import settings

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_number TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                intent TEXT,
                confidence REAL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_number TEXT NOT NULL,
                name TEXT,
                preferred_date TEXT,
                preferred_time TEXT,
                purpose TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_number TEXT PRIMARY KEY,
                name TEXT,
                last_seen TEXT,
                pending_meeting_step TEXT
            )
        """)
        conn.commit()

@contextmanager
def get_conn():
    conn = sqlite3.connect(settings.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def save_conversation(user_number, user_message, ai_response, intent, confidence):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO conversations (user_number, user_message, ai_response, intent, confidence, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_number, user_message, ai_response, intent, confidence, datetime.now().isoformat())
        )
        conn.commit()

def get_recent_history(user_number, limit=6):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT user_message, ai_response FROM conversations WHERE user_number=? ORDER BY id DESC LIMIT ?",
            (user_number, limit)
        ).fetchall()
        return list(reversed(rows))

def search_conversations(keyword):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM conversations WHERE user_message LIKE ? OR ai_response LIKE ? ORDER BY id DESC",
            (f"%{keyword}%", f"%{keyword}%")
        ).fetchall()

def save_meeting(user_number, name, date, time, purpose):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO meetings (user_number, name, preferred_date, preferred_time, purpose, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_number, name, date, time, purpose, datetime.now().isoformat())
        )
        conn.commit()

def get_all_meetings(status=None):
    with get_conn() as conn:
        if status:
            return conn.execute("SELECT * FROM meetings WHERE status=? ORDER BY id DESC", (status,)).fetchall()
        return conn.execute("SELECT * FROM meetings ORDER BY id DESC").fetchall()

def upsert_user_state(user_number, **kwargs):
    with get_conn() as conn:
        existing = conn.execute("SELECT user_number FROM users WHERE user_number=?", (user_number,)).fetchone()
        now = datetime.now().isoformat()
        if existing:
            fields = ", ".join(f"{k}=?" for k in kwargs)
            conn.execute(f"UPDATE users SET last_seen=?, {fields} WHERE user_number=?",
                         (now, *kwargs.values(), user_number))
        else:
            conn.execute("INSERT INTO users (user_number, last_seen, name, pending_meeting_step) VALUES (?, ?, ?, ?)",
                         (user_number, now, kwargs.get("name"), kwargs.get("pending_meeting_step")))
        conn.commit()

def get_user_state(user_number):
    with get_conn() as conn:
        return conn.execute("SELECT * FROM users WHERE user_number=?", (user_number,)).fetchone()
