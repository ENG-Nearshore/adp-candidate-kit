"""Domain model of the triage service."""

from dataclasses import dataclass, field
from datetime import date

PRIORITIES = ("Low", "Normal", "High", "Critical")
STATUSES = ("Open", "In Progress", "Resolved")


@dataclass(frozen=True)
class Ticket:
    id: str
    title: str
    description: str
    priority: str
    status: str
    opened_on: date
    customer_area: str

    @property
    def text(self) -> str:
        return f"{self.title}. {self.description}"


@dataclass(frozen=True)
class Classification:
    category: str
    urgency: str
    summary: str


@dataclass
class TriagedTicket:
    ticket: Ticket
    classification: Classification
    group_id: str | None = None


@dataclass
class Group:
    id: str
    label: str
    ticket_ids: list[str] = field(default_factory=list)
