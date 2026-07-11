"""
Minimal admin API -- protected by a single shared password (fine for a
4-day intern project; note in your README this would use real auth in
production). Powers the admin dashboard bonus feature.
"""
from fastapi import APIRouter, HTTPException, Header
from config.settings import settings
from database.db import search_conversations, get_all_meetings, get_conn
from chatbot.knowledge_retrieval import kb

router = APIRouter()

def check_admin(x_admin_password: str = Header(None)):
    if x_admin_password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin password")

@router.get("/admin/conversations")
def list_conversations(keyword: str = "", x_admin_password: str = Header(None)):
    check_admin(x_admin_password)
    if keyword:
        rows = search_conversations(keyword)
    else:
        with get_conn() as conn:
            rows = conn.execute("SELECT * FROM conversations ORDER BY id DESC LIMIT 100").fetchall()
    return [dict(r) for r in rows]

@router.get("/admin/meetings")
def list_meetings(status: str = None, x_admin_password: str = Header(None)):
    check_admin(x_admin_password)
    rows = get_all_meetings(status)
    return [dict(r) for r in rows]

@router.post("/admin/knowledge-base/reload")
def reload_kb(x_admin_password: str = Header(None)):
    check_admin(x_admin_password)
    kb.reload()
    return {"status": "knowledge base reloaded", "entries": len(kb.entries)}
