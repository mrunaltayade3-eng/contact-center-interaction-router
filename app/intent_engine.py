"""Deterministic English phrase matcher, NOT Amazon Lex or a trained model."""
import re
from app.models import Understanding

# Specific/risk-sensitive intents precede more general requests.
PATTERNS = {
    "fraud": [r"fraud", r"stolen card", r"stole my card", r"unauthorized", r"don\'t recognize", r"do not recognize", r"did not make"],
    "payment_dispute": [r"charged twice", r"charge my card twice", r"duplicate (?:charge|payment)", r"wrong charge", r"charged.*twice"],
    "refund_request": [r"refund", r"money back"],
    "account_access": [r"password", r"locked out", r"can\'t (?:log|sign) in", r"cannot (?:log|sign) in"],
    "technical_support": [r"not working", r"crash(?:es|ed|ing)?", r"error", r"connection", r"app is down"],
    "order_status": [r"track.*order", r"order status", r"where is my order", r"delivery"],
    "cancellation": [r"cancel(?:lation)?", r"unsubscribe"],
}

def normalize(text: str) -> str:
    return " ".join(text.lower().replace("’", "'").split())

def contains(text: str, pattern: str) -> bool:
    return re.search(r"\b(?:" + pattern + r")\b", text) is not None

def extract_slots(text: str) -> dict[str, str]:
    slots = {}
    amount = re.search(r"\$((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?)(?![\d.])", text)
    if amount:
        slots.update(amount=amount[1].replace(",", ""), currency="USD")
    order = re.search(r"\border\s*(?:id\s*[:#]?|#)\s*([a-z0-9][a-z0-9-]*)\b", text, re.I)
    if order:
        slots["order_id"] = order[1].upper()
    date = re.search(r"\b(?:today|yesterday|\d{4}-\d{2}-\d{2})\b", text)
    if date:
        slots["date_mention"] = date[0]  # Raw mention, not a validated/resolved date.
    return slots

def recognize(message: str) -> Understanding:
    text = normalize(message)
    matches = {intent: [p for p in patterns if contains(text, p)]
               for intent, patterns in PATTERNS.items()}
    intents = [i for i, hits in matches.items() if hits]
    intent = intents[0] if intents else "unknown"
    return Understanding(intent=intent, matched_intents=intents,
                         evidence=matches.get(intent, []), slots=extract_slots(text))
