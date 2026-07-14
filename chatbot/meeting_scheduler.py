"""
Simple stateful meeting-request flow driven by users.pending_meeting_step.
This is intentionally state-machine-based (not another AI call) --
scheduling should be deterministic and reliable, not left to LLM guessing.
"""
from database.db import save_meeting, upsert_user_state, get_user_state

STEPS = ["ask_name", "ask_date", "ask_time", "ask_purpose", "done"]

def start_meeting_flow(user_number):
    upsert_user_state(user_number, pending_meeting_step="ask_name")
    return "Sure, let's schedule a meeting. What's your name?"

def handle_meeting_step(user_number, message):
    """Returns (reply_text, is_meeting_flow_complete)."""
    state = get_user_state(user_number)
    step = state["pending_meeting_step"] if state else None

    if step == "ask_name":
        upsert_user_state(user_number, pending_meeting_step="ask_date:" + message.strip())
        return "Got it. What date works for you? (e.g. 15 July)", False

    if step and step.startswith("ask_date:"):
        name = step.split(":", 1)[1]
        upsert_user_state(user_number, pending_meeting_step=f"ask_time:{name}|{message.strip()}")
        return "What time works best?", False

    if step and step.startswith("ask_time:"):
        name, date = step.split(":", 1)[1].split("|")
        upsert_user_state(user_number, pending_meeting_step=f"ask_purpose:{name}|{date}|{message.strip()}")
        return "Last thing -- what's the purpose of the meeting?", False

    if step and step.startswith("ask_purpose:"):
        name, date, time = step.split(":", 1)[1].split("|")
        purpose = message.strip()
        save_meeting(user_number, name, date, time, purpose)
        upsert_user_state(user_number, pending_meeting_step=None)
        return (f"Meeting request confirmed:\n"
                f"Name: {name}\nDate: {date}\nTime: {time}\nPurpose: {purpose}\n\n"
                f"Our team will follow up to finalize this."), True

    return "Something went wrong with scheduling -- let's start over. Just say 'schedule a meeting'.", True

def is_in_meeting_flow(user_number):
    state = get_user_state(user_number)
    return bool(state and state["pending_meeting_step"])
