"""Transparent transcript heuristics, independent of speech synthesis."""
from app.intent_engine import contains, normalize
from app.models import Analysis

NEGATIVE = [r"angry", r"frustrated", r"terrible", r"unacceptable", r"not happy", r"still (?:not|isn't) resolved", r"nobody has fixed"]
POSITIVE = [r"thank you", r"thanks", r"great", r"happy"]
REPEAT = [r"calling again", r"contacting again", r"called (?:before|twice|three times)", r"third time", r"already (?:spoke|talked)", r"follow(?:ing)? up"]
ESCALATE = [r"manager", r"supervisor", r"formal complaint"]

def analyze(message: str, previous_contacts: int = 0) -> Analysis:
    text = normalize(message)
    negative = any(contains(text, p) for p in NEGATIVE)
    # Suppress common negations; this is intentionally not general language understanding.
    positive_text = text.replace("not happy", "").replace("not great", "")
    positive = any(contains(positive_text, p) for p in POSITIVE)
    repeat = previous_contacts > 0 or any(contains(text, p) for p in REPEAT)
    explicit = any(contains(text, p) for p in ESCALATE)
    risk = explicit or previous_contacts >= 2 or (negative and repeat)
    signals = []
    for present, label in [(negative, "negative_language"), (positive, "positive_language"),
                           (previous_contacts > 0, "provided_contact_history"),
                           (any(contains(text, p) for p in REPEAT), "repeat_contact_phrase"),
                           (explicit, "supervisor_request")]:
        if present:
            signals.append(label)
    return Analysis(sentiment="mixed" if negative and positive else "negative" if negative else "positive" if positive else "neutral",
                    repeat_contact=repeat, escalation_risk=risk, signals=signals)
