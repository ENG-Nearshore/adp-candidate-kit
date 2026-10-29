"""Deterministic, offline classifier based on keyword lists."""

from triage.core.models import Classification, Ticket

CATEGORY_KEYWORDS = {
    "access": ("login", "password", "account", "locked", "portal"),
    "billing": ("invoice", "charge", "charged", "refund", "payment", "tariff"),
    "metering": ("meter", "reading", "readings", "smart"),
    "outage": ("outage", "power", "supply", "map"),
}

URGENCY_BY_PRIORITY = {"Critical": "high", "High": "high", "Normal": "medium", "Low": "low"}


class KeywordClassifier:
    def classify(self, ticket: Ticket) -> Classification:
        category, _ = self._best_category(ticket)
        return Classification(
            category=category,
            urgency=URGENCY_BY_PRIORITY.get(ticket.priority, "medium"),
            summary=ticket.title[:80],
        )

    def explain(self, ticket: Ticket) -> str:
        category, hits = self._best_category(ticket)
        if not hits:
            return f"No category keywords found in {ticket.id}; classified as '{category}'."
        return f"{ticket.id} classified as '{category}' because it mentions: {', '.join(hits)}."

    @staticmethod
    def _best_category(ticket: Ticket) -> tuple[str, list[str]]:
        words = set(ticket.text.lower().replace(".", " ").replace(",", " ").split())
        best, best_hits = "other", []
        for category, keywords in CATEGORY_KEYWORDS.items():
            hits = [k for k in keywords if k in words]
            if len(hits) > len(best_hits):
                best, best_hits = category, hits
        return best, best_hits
