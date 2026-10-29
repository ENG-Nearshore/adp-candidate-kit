"""Lets only one classifier call run at a time.

The model gateway used in production processes a single request at a time and
returns errors under concurrent load.
"""

import threading

from triage.core.models import Classification, Ticket


class SerializedClassifier:
    def __init__(self, inner):
        self._inner = inner
        self._lock = threading.Lock()

    def classify(self, ticket: Ticket) -> Classification:
        with self._lock:
            return self._inner.classify(ticket)

    def explain(self, ticket: Ticket) -> str:
        with self._lock:
            return self._inner.explain(ticket)
