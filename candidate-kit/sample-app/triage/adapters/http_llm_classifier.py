"""Classifier backed by a chat-completions model gateway."""

import json
import urllib.error
import urllib.request

from triage.core.models import Classification, Ticket

CLASSIFY_PROMPT = (
    "You triage utility-company support tickets. Reply with JSON only: "
    '{"category": one of access|billing|metering|outage|other, '
    '"urgency": one of low|medium|high, "summary": at most 80 characters}.'
)
EXPLAIN_PROMPT = "Explain in two sentences how this support ticket should be categorised and why."


class ClassifierError(RuntimeError):
    pass


class HttpLlmClassifier:
    def __init__(self, base_url: str, model: str, api_key: str | None, timeout_seconds: float):
        self._url = base_url.rstrip("/") + "/chat/completions"
        self._model = model
        self._api_key = api_key
        self._timeout = timeout_seconds

    def classify(self, ticket: Ticket) -> Classification:
        content = self._chat(CLASSIFY_PROMPT, ticket)
        try:
            data = json.loads(content)
            return Classification(
                category=data["category"], urgency=data["urgency"], summary=data["summary"][:80]
            )
        except (ValueError, KeyError, TypeError) as exc:
            raise ClassifierError(f"Unparseable classification for {ticket.id}: {content!r}") from exc

    def explain(self, ticket: Ticket) -> str:
        return self._chat(EXPLAIN_PROMPT, ticket)

    def _chat(self, system_prompt: str, ticket: Ticket) -> str:
        payload = {
            "model": self._model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{ticket.title}\n\n{ticket.description}"},
            ],
        }
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        request = urllib.request.Request(
            self._url, data=json.dumps(payload).encode(), headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                body = json.load(response)
        except (urllib.error.URLError, TimeoutError) as exc:
            raise ClassifierError(f"Model gateway unavailable: {exc}") from exc
        return body["choices"][0]["message"]["content"]
