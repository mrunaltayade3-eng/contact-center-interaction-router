from fastapi import FastAPI
from app.models import Interaction, RoutingResult
from app.router import route

app = FastAPI(title="Contact-Center Interaction Router", version="1.0.0",
              description="Local rule-based routing prototype. No AWS credentials required; no live queue transfer or audio generation.")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "local"}

@app.post("/route", response_model=RoutingResult)
def route_interaction(interaction: Interaction) -> RoutingResult:
    return route(interaction)
