"""Manual re-assignment of a ticket to another group."""

from triage.core.models import TriagedTicket
from triage.core.ports import TicketRepository


class ReassignTicket:
    def __init__(self, repository: TicketRepository):
        self._repository = repository

    def execute(self, ticket_id: str, target_group_id: str) -> TriagedTicket:
        triaged = self._repository.get_ticket(ticket_id)
        if triaged is None:
            raise KeyError(f"Unknown ticket {ticket_id}")
        target = self._repository.get_group(target_group_id)
        if target is None:
            raise KeyError(f"Unknown group {target_group_id}")

        if triaged.group_id:
            previous = self._repository.get_group(triaged.group_id)
            if previous and ticket_id in previous.ticket_ids:
                previous.ticket_ids.remove(ticket_id)
        target.ticket_ids.append(ticket_id)
        self._repository.assign_group(ticket_id, target_group_id)
        return self._repository.get_ticket(ticket_id)
