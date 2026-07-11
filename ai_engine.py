"""
Gemini wrapper. Builds a prompt from: recent conversation history +
(optional) retrieved knowledge base context, so replies stay on-topic
and business-accurate instead of generic chatbot filler.
"""
import google.generativeai as genai
from config.settings import settings
from database.db import get_recent_history

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """You are the official WhatsApp Executive Assistant for
Positiveway Solutions Pvt. Ltd. Be professional, warm, and concise (WhatsApp
replies should be short -- 2 to 5 sentences unless the user asks for detail).
Never invent facts about the company that aren't given to you in context.
If you don't have enough information, say so honestly and offer to connect
the user with the team."""

def generate_reply(user_number, user_message, kb_context=None, kb_confident=True):
    history = get_recent_history(user_number)
    history_text = "\n".join(f"User: {h['user_message']}\nAssistant: {h['ai_response']}" for h in history)

    context_block = ""
    if kb_context:
        context_block = "Relevant company knowledge:\n" + "\n".join(
            f"- {c['topic']}: {c['content']}" for c in kb_context
        )
    elif not kb_confident:
        context_block = ("No confident match was found in the knowledge base for this question. "
                          "Be honest that you're not certain, and offer to have the team follow up.")

    prompt = f"""{SYSTEM_PROMPT}

{context_block}

Recent conversation:
{history_text}

User's new message: {user_message}

Reply as the assistant:"""

    response = model.generate_content(prompt)
    return response.text.strip()
