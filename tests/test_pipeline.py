import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Interaction
from app.intent_engine import recognize
from app.router import route
from app.sentiment import analyze
from app.kpis import summarize

client = TestClient(app)

@pytest.mark.parametrize("message,intent,queue", [
    ("stolen card", "fraud", "fraud"),
    ("charged twice", "payment_dispute", "billing"),
    ("refund", "refund_request", "billing"),
    ("forgot password", "account_access", "account"),
    ("app crashes", "technical_support", "technical"),
    ("order status", "order_status", "orders"),
    ("cancel subscription", "cancellation", "retention"),
    ("hello", "unknown", "general_support"),
])
def test_routes(message, intent, queue):
    result = route(Interaction(customer_id="demo", message=message))
    assert result.understanding.intent == intent
    assert result.queue == queue

def test_fraud_overrides_refund():
    result = recognize("Refund this unauthorized charge")
    assert result.intent == "fraud"
    assert result.matched_intents == ["fraud", "refund_request"]

def test_boundaries_and_normalization():
    assert recognize("I don’t recognize this").intent == "fraud"
    assert recognize("This is errorless").intent == "unknown"
    assert recognize("CHARGED   TWICE").intent == "payment_dispute"

def test_slots():
    assert recognize("Refund $1,250.00 for order #AB-12 yesterday").slots == {
        "amount": "1250.00", "currency": "USD", "order_id": "AB-12", "date_mention": "yesterday"}
    assert recognize("hello").slots == {}

@pytest.mark.parametrize("message,count,repeat,risk", [
    ("hello", 0, False, False), ("hello", 1, True, False),
    ("hello", 2, True, True), ("calling again", 0, True, False),
    ("frustrated and calling again", 0, True, True),
    ("need supervisor", 0, False, True),
])
def test_contact_and_escalation(message, count, repeat, risk):
    analysis = analyze(message, count)
    assert analysis.repeat_contact is repeat
    assert analysis.escalation_risk is risk

@pytest.mark.parametrize("text,expected", [("not happy", "negative"), ("thanks", "positive"),
    ("thank you but terrible", "mixed"), ("hello", "neutral")])
def test_sentiment(text, expected):
    assert analyze(text).sentiment == expected

def test_priority_cap_and_specialist_preserved():
    result = route(Interaction(customer_id="demo", message="urgent fraud, frustrated, need manager", previous_contacts=3))
    assert (result.priority_score, result.priority, result.queue) == (100, "critical", "fraud")
    assert result.analysis.escalation_risk

@pytest.mark.parametrize("message,score,priority", [("order status",10,"low"),
    ("password",30,"medium"), ("charged twice",50,"high"), ("fraud",80,"critical")])
def test_priority_levels(message, score, priority):
    result = route(Interaction(customer_id="demo", message=message))
    assert (result.priority_score,result.priority) == (score,priority)

@pytest.mark.parametrize("payload", [
    {"customer_id":"", "message":"hello"}, {"customer_id":"c", "message":"   "},
    {"customer_id":"c", "message":"x"*4001},
    {"customer_id":"c", "message":"hello", "previous_contacts":-1},
    {"customer_id":"c", "message":"hello", "previous_contacts":True},
    {"customer_id":"c", "message":"hello", "unknown_field":1}, {},
])
def test_api_validation(payload):
    assert client.post("/route",json=payload).status_code == 422

def test_api_contract_and_no_fake_audio():
    assert client.get("/health").json() == {"status":"ok","mode":"local"}
    response = client.post("/route",json={"customer_id":"DEMO-001", "message":"charged twice"})
    assert response.status_code == 200
    result = response.json()
    assert result["queue"] == "billing"
    assert result["speech"]["audio_generated"] is False
    assert result["speech"]["text"] == result["response"]
    assert "/route" in client.get("/openapi.json").json()["paths"]

def test_stateless_history():
    payload = {"customer_id":"same-customer", "message":"hello"}
    assert client.post("/route",json=payload).json() == client.post("/route",json=payload).json()

def test_empty_kpis():
    assert summarize([])["routing_accuracy"] is None
    assert summarize([])["total_interactions"] == 0

def test_kpi_denominators():
    rows = [{"customer_id":"a", "message":"fraud", "previous_contacts":"1", "expected_intent":"fraud", "expected_queue":"fraud"},
            {"customer_id":"b", "message":"hello", "previous_contacts":"0", "expected_intent":"refund_request", "expected_queue":"billing"}]
    result = summarize(rows)
    assert result["intent_accuracy"] == 0.5
    assert result["routing_accuracy"] == 0.5
    assert result["repeat_contact_signal_rate"] == 0.5
    assert sum(result["queue_distribution"].values()) == 2
