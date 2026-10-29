"""Escalation policy for stale critical tickets."""

from datetime import date

from triage.core.models import Ticket

ESCALATED_PRIORITY = "Critical"
CLOSED_STATUS = "Resolved"


def find_escalations(tickets: list[Ticket], today: date, escalation_days: int) -> list[tuple[Ticket, int]]:
    """Return (ticket, age in days) for every critical ticket that is not resolved
    and has been open for more than `escalation_days` days."""
    escalations = []
    for ticket in tickets:
        if ticket.priority != ESCALATED_PRIORITY or ticket.status == CLOSED_STATUS:
            continue
        age_days = (today - ticket.opened_on).days
        if age_days > escalation_days:
            escalations.append((ticket, age_days))
    return escalations
