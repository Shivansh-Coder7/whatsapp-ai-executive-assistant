"""
FastAPI routes for the Twilio WhatsApp Sandbox webhook.
Twilio POSTs form-encoded data (not JSON) to this endpoint on every
incoming WhatsApp message -- that's why we use Request.form(), not
a Pydantic body model.
"""
from fastapi import APIRouter, Request, Response
from twilio.twiml.messaging_response import MessagingResponse

from chatbot.intent_router import detect_intent
from chatbot.knowledge_retrieval import kb
from chatbot.ai_engine import generate_reply
from chatbot.meeting_scheduler import start_meeting_flow, handle_meeting_step, is_in_meeting_flow
from database.db import save_conversation

router = APIRouter()

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    incoming_msg = form.get("Body", "").strip()
    user_number = form.get("From", "")

    reply_text = handle_incoming_message(user_number, incoming_msg)

    twiml = MessagingResponse()
    twiml.message(reply_text)
    return Response(content=str(twiml), media_type="application/xml")


def handle_incoming_message(user_number: str, incoming_msg: str) -> str:
    try:
        if is_in_meeting_flow(user_number):
            reply_text, _ = handle_meeting_step(user_number, incoming_msg)
            save_conversation(user_number, incoming_msg, reply_text, "meeting_request", 1.0)
            return reply_text

        intent = detect_intent(incoming_msg)

        if intent == "meeting_request":
            reply_text = start_meeting_flow(user_number)
            save_conversation(user_number, incoming_msg, reply_text, intent, 1.0)
            return reply_text

        matches, confidence = kb.search(incoming_msg)
        confident = kb.is_confident(confidence)
        reply_text = generate_reply(
            user_number, incoming_msg,
            kb_context=matches if confident else None,
            kb_confident=confident
        )
        save_conversation(user_number, incoming_msg, reply_text, intent, confidence)
        return reply_text
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"DEBUG ERROR: {type(e).__name__}: {str(e)}"
