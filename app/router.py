from app.intent_engine import contains, normalize, recognize
from app.models import Interaction, RoutingResult
from app.sentiment import analyze

RULES = {
    "fraud": (80, "fraud"), "payment_dispute": (50, "billing"),
    "refund_request": (30, "billing"), "account_access": (30, "account"),
    "technical_support": (30, "technical"), "order_status": (10, "orders"),
    "cancellation": (20, "retention"), "unknown": (20, "general_support"),
}

def route(interaction: Interaction) -> RoutingResult:
    understanding = recognize(interaction.message)
    analysis = analyze(interaction.message, interaction.previous_contacts)
    score, queue = RULES[understanding.intent]
    reasons = [f"intent:{understanding.intent} (+{score})"]
    for active, points, reason in [
        (analysis.sentiment in ("negative", "mixed"), 10, "negative_sentiment"),
        (analysis.repeat_contact, 15, "repeat_contact"),
        (analysis.escalation_risk, 20, "escalation_risk"),
        (contains(normalize(interaction.message), r"urgent|immediately|emergency"), 10, "urgency"),
    ]:
        if active:
            score += points
            reasons.append(f"{reason} (+{points})")
    score = min(score, 100)
    priority = "critical" if score >= 80 else "high" if score >= 50 else "medium" if score >= 25 else "low"
    response = (f"Recommended next step: connect you with our {queue.replace('_', ' ')} team. "
                "A support agent will review your request.")
    return RoutingResult(customer_id=interaction.customer_id, understanding=understanding,
                         analysis=analysis, priority_score=score, priority=priority,
                         queue=queue, reasons=reasons, response=response,
                         speech={"provider": "mock", "audio_generated": False, "text": response})
