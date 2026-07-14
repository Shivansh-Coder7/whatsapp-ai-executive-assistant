"""
Routes an incoming message to: meeting scheduler, internship flow,
knowledge base + AI, or a plain AI reply. Kept as simple rule-based
routing on purpose -- fast, free (no extra API call), and predictable,
which matters more than cleverness for a 4-day deadline.
"""
import re

MEETING_TRIGGERS = ["schedule a meeting", "book a meeting", "set up a call", "schedule meeting", "meet with"]
INTERNSHIP_TRIGGERS = ["internship", "intern", "apply for internship", "resume"]

def detect_intent(message: str) -> str:
    text = message.lower().strip()
    if any(t in text for t in MEETING_TRIGGERS):
        return "meeting_request"
    if any(t in text for t in INTERNSHIP_TRIGGERS):
        return "internship_query"
    return "general_query"
