"""Runtime settings, read once from environment variables at startup."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    port: int
    api_token: str
    tickets_csv: str
    classifier: str
    llm_base_url: str
    llm_model: str
    llm_api_key: str | None
    llm_timeout_seconds: float
    similarity_threshold: float
    escalation_days: int
    escalation_webhook_url: str | None


def load_settings() -> Settings:
    return Settings(
        port=int(os.getenv("TRIAGE_PORT", "8085")),
        api_token=os.getenv("TRIAGE_API_TOKEN", "local-dev-token"),
        tickets_csv=os.getenv("TRIAGE_TICKETS_CSV", "fixtures/tickets.csv"),
        # "keyword" (offline, default) or "llm"
        classifier=os.getenv("TRIAGE_CLASSIFIER", "keyword"),
        llm_base_url=os.getenv("LLM_BASE_URL", "http://10.40.7.21:8000/v1"),
        llm_model=os.getenv("LLM_MODEL", "triage-small"),
        llm_api_key=os.getenv("LLM_API_KEY") or None,
        llm_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
        similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.82")),
        escalation_days=int(os.getenv("ESCALATION_DAYS", "3")),
        escalation_webhook_url=os.getenv("ESCALATION_WEBHOOK_URL") or None,
    )
