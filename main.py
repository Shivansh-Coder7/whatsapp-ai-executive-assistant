"""
Entry point. Run with:  uvicorn main:app --reload
Then expose it publicly with ngrok (see README) and paste the ngrok URL
+ /webhook/whatsapp into your Twilio Sandbox webhook config.
"""
from fastapi import FastAPI
from database.db import init_db
from app.whatsapp_webhook import router as whatsapp_router
from app.admin_routes import router as admin_router

app = FastAPI(title="Positiveway AI WhatsApp Executive Assistant")

init_db()

app.include_router(whatsapp_router)
app.include_router(admin_router)

@app.get("/")
def health_check():
    return {"status": "running", "service": "AI WhatsApp Executive Assistant"}
