"""
Central config loader. Every other module reads settings from here
instead of calling os.getenv() everywhere -- makes it trivial to
swap Gemini for Groq/OpenRouter later without touching business logic.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme123")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "database/assistant.db")
    KB_CONFIDENCE_THRESHOLD = float(os.getenv("KB_CONFIDENCE_THRESHOLD", "0.25"))

settings = Settings()
