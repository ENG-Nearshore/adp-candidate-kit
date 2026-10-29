"""Interfaces the core depends on. Adapters in triage.adapters implement them."""

from typing import Protocol

from triage.core.models import Classification, Group, Ticket, TriagedTicket


class TicketSource(Protocol):
    def load_all(self) -> list[Ticket]:
        ...


class Classifier(Protocol):
    def classify(self, ticket: Ticket) -> Classification:
        ...

    def explain(self, ticket: Ticket) -> str:
        ...


class TicketRepository(Protocol):
    def clear(self) -> None:
        ...

    def save_ticket(self, triaged: TriagedTicket) -> None:
        ...

    def get_ticket(self, ticket_id: str) -> TriagedTicket | None:
        ...

    def list_tickets(self, status: str | None = None) -> list[TriagedTicket]:
        ...

    def assign_group(self, ticket_id: str, group_id: str | None) -> None:
        ...

    def save_group(self, group: Group) -> None:
        ...

    def get_group(self, group_id: str) -> Group | None:
        ...

    def list_groups(self) -> list[Group]:
        ...


class Notifier(Protocol):
    def notify_escalation(self, ticket: Ticket, age_days: int) -> None:
        ...
