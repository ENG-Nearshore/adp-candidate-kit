"""Ticket endpoints."""

from triage.api.router import Router
from triage.core.models import STATUSES
from triage.core.ports import Classifier, TicketRepository
from triage.core.triage_service import TriageService

TICKET_ID = r"(?P<ticket_id>LU-\d+)"


def register(router: Router, repository: TicketRepository, triage_service: TriageService, explainer: Classifier) -> None:
    def list_tickets(params, query, body):
        status = query.get("status")
        if status is not None and status not in STATUSES:
            return 400, {"error": f"status must be one of {list(STATUSES)}"}
        return 200, repository.list_tickets(status)

    def get_ticket(params, query, body):
        triaged = repository.get_ticket(params["ticket_id"])
        if triaged is None:
            return 404, {"error": "ticket not found"}
        return 200, triaged

    def explain_ticket(params, query, body):
        triaged = repository.get_ticket(params["ticket_id"])
        if triaged is None:
            return 404, {"error": "ticket not found"}
        return 200, {"ticket_id": triaged.ticket.id, "explanation": explainer.explain(triaged.ticket)}

    def run_triage(params, query, body):
        return 200, triage_service.run()

    router.add("GET", "/tickets", list_tickets)
    router.add("GET", f"/tickets/{TICKET_ID}", get_ticket)
    router.add("GET", f"/tickets/{TICKET_ID}/explanation", explain_ticket)
    router.add("POST", "/triage/run", run_triage)
