"""Sends escalation events to the dispatch team's webhook."""

import json
import logging
import urllib.error
import urllib.request

from triage.core.models import Ticket

log = logging.getLogger(__name__)


class WebhookNotifier:
    def __init__(self, url: str | None, timeout_seconds: float = 5.0):
        self._url = url
        self._timeout = timeout_seconds

    def notify_escalation(self, ticket: Ticket, age_days: int) -> None:
        if not self._url:
            log.info("Escalation webhook not configured; skipping %s", ticket.id)
            return
        payload = {
            "event": "ticket.escalated",
            "ticket_id": ticket.id,
            "title": ticket.title,
            "priority": ticket.priority,
            "age_days": age_days,
        }
        request = urllib.request.Request(
            self._url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout):
                pass
        except (urllib.error.URLError, TimeoutError) as exc:
            log.warning("Escalation for %s not delivered: %s", ticket.id, exc)
