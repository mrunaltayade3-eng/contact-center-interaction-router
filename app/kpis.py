"""Run: python -m app.kpis --input data/sample_interactions.csv"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from app.models import Interaction
from app.router import route

REQUIRED = {"interaction_id", "customer_id", "message", "previous_contacts", "expected_intent", "expected_queue"}

def summarize(rows: list[dict]) -> dict:
    results = [route(Interaction(customer_id=r["customer_id"], message=r["message"],
                                 previous_contacts=int(r["previous_contacts"]))) for r in rows]
    n = len(results)
    def rate(count):
        return round(count / n, 4) if n else None
    return {
        "dataset": "synthetic_demo", "total_interactions": n,
        "intent_accuracy": rate(sum(x.understanding.intent == r["expected_intent"] for x, r in zip(results, rows))),
        "routing_accuracy": rate(sum(x.queue == r["expected_queue"] for x, r in zip(results, rows))),
        "repeat_contact_signal_rate": rate(sum(x.analysis.repeat_contact for x in results)),
        "escalation_risk_rate": rate(sum(x.analysis.escalation_risk for x in results)),
        "negative_or_mixed_sentiment_rate": rate(sum(x.analysis.sentiment in ("negative", "mixed") for x in results)),
        "queue_distribution": dict(sorted(Counter(x.queue for x in results).items())),
        "priority_distribution": dict(sorted(Counter(x.priority for x in results).items())),
        "repeat_signals_by_queue": dict(sorted(Counter(x.queue for x in results if x.analysis.repeat_contact).items())),
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/sample_interactions.csv"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with args.input.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not REQUIRED.issubset(reader.fieldnames or []):
            parser.error("CSV missing required columns: " + ", ".join(sorted(REQUIRED)))
        rows = list(reader)
    ids = [r["interaction_id"] for r in rows]
    if len(ids) != len(set(ids)):
        parser.error("interaction_id must be unique; duplicate events would distort KPIs")
    result = json.dumps(summarize(rows), indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    print(result, end="")

if __name__ == "__main__":
    main()
