# AI WhatsApp Executive Assistant 

## What makes this build different
Instead of keyword matching against the knowledge base, this project uses
TF-IDF + cosine similarity (`chatbot/knowledge_retrieval.py`) to find the
most relevant company info for a user's question, and only lets Gemini use
that context when the match confidence clears a threshold. Below threshold,
the assistant honestly says it isn't sure instead of guessing -- this is
the "confidence-based escalation" behavior mentioned in the project report.

## Setup

1. **Clone & install**
   ```
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Get a Gemini API key**
   Go to https://aistudio.google.com/app/apikey -> Create API key.

3. **Set up Twilio WhatsApp Sandbox**
   - Create a free Twilio account: https://www.twilio.com/try-twilio
   - Go to Messaging -> Try it out -> Send a WhatsApp message
   - Follow the "join <your-sandbox-code>" instructions to link your own
     WhatsApp number to the sandbox (send that message from your phone)
   - Copy your Account SID and Auth Token from the Twilio Console

4. **Configure environment**
   ```
   cp .env.example .env
   ```
   Fill in `GEMINI_API_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`.

5. **Run the server**
   ```
   uvicorn main:app --reload
   ```

6. **Expose it publicly with ngrok** (Twilio needs a public URL)
   ```
   ngrok http 8000
   ```
   Copy the `https://xxxx.ngrok-free.app` URL.

7. **Connect Twilio to your webhook**
   In Twilio Console -> WhatsApp Sandbox Settings, set
   "WHEN A MESSAGE COMES IN" to:
   `https://xxxx.ngrok-free.app/webhook/whatsapp`
   Method: POST. Save.

8. **Test it**
   Message your Twilio Sandbox number from WhatsApp. It should reply.

## Editing the knowledge base
Edit `knowledge_base/company_info.json` directly (no code changes needed),
then call `POST /admin/knowledge-base/reload` with header
`x-admin-password: <ADMIN_PASSWORD>` to pick up changes without restarting.

## Admin endpoints
- `GET /admin/conversations?keyword=xyz`
- `GET /admin/meetings?status=pending`
- `POST /admin/knowledge-base/reload`
All require header: `x-admin-password: <your ADMIN_PASSWORD from .env>`

## Project structure
```
AI-WhatsApp-Assistant/
├── app/                  # FastAPI routes (webhook, admin)
├── chatbot/               # AI engine, intent routing, KB retrieval, scheduler
├── database/               # SQLite models + queries
├── knowledge_base/         # Editable company_info.json
├── config/                 # Settings loader
├── main.py
├── requirements.txt
└── .env.example
```
