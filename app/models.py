from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Intent = Literal["fraud", "payment_dispute", "refund_request", "account_access", "technical_support", "order_status", "cancellation", "unknown"]

class Interaction(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    customer_id: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=4000)
    previous_contacts: int = Field(default=0, ge=0, le=10000, strict=True)

class Understanding(BaseModel):
    intent: Intent
    matched_intents: list[Intent]
    evidence: list[str]
    slots: dict[str, str]

class Analysis(BaseModel):
    sentiment: Literal["positive", "negative", "neutral", "mixed"]
    repeat_contact: bool
    escalation_risk: bool
    signals: list[str]

class RoutingResult(BaseModel):
    customer_id: str
    understanding: Understanding
    analysis: Analysis
    priority_score: int
    priority: Literal["low", "medium", "high", "critical"]
    queue: str
    reasons: list[str]
    response: str
    speech: dict[str, str | bool]
