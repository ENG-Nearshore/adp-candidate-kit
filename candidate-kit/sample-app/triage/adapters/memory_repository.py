"""In-memory storage. Contents are lost when the process stops."""

import threading

from triage.core.models import Group, TriagedTicket


class InMemoryRepository:
    def __init__(self):
        self._tickets: dict[str, TriagedTicket] = {}
        self._groups: dict[str, Group] = {}
        self._lock = threading.Lock()

    def clear(self) -> None:
        with self._lock:
            self._tickets.clear()
            self._groups.clear()

    def save_ticket(self, triaged: TriagedTicket) -> None:
        with self._lock:
            self._tickets[triaged.ticket.id] = triaged

    def get_ticket(self, ticket_id: str) -> TriagedTicket | None:
        return self._tickets.get(ticket_id)

    def list_tickets(self, status: str | None = None) -> list[TriagedTicket]:
        items = sorted(self._tickets.values(), key=lambda t: t.ticket.id)
        return [t for t in items if status is None or t.ticket.status == status]

    def assign_group(self, ticket_id: str, group_id: str | None) -> None:
        with self._lock:
            self._tickets[ticket_id].group_id = group_id

    def save_group(self, group: Group) -> None:
        with self._lock:
            self._groups[group.id] = group

    def get_group(self, group_id: str) -> Group | None:
        return self._groups.get(group_id)

    def list_groups(self) -> list[Group]:
        return sorted(self._groups.values(), key=lambda g: g.id)
