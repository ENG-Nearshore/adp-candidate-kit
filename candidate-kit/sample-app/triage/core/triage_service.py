"""Runs a full triage pass over the ticket export."""

import logging
from collections.abc import Callable
from datetime import date

from triage.core.escalation import find_escalations
from triage.core.grouping import group_tickets
from triage.core.models import TriagedTicket
from triage.core.ports import Classifier, Notifier, TicketRepository, TicketSource

log = logging.getLogger(__name__)


class TriageService:
    def __init__(
        self,
        source: TicketSource,
        classifier: Classifier,
        repository: TicketRepository,
        notifier: Notifier,
        similarity_threshold: float,
        escalation_days: int,
        clock: Callable[[], date] = date.today,
    ):
        self._source = source
        self._classifier = classifier
        self._repository = repository
        self._notifier = notifier
        self._similarity_threshold = similarity_threshold
        self._escalation_days = escalation_days
        self._clock = clock

    def run(self) -> dict:
        tickets = self._source.load_all()
        self._repository.clear()

        # Tickets are stored one by one as soon as they are classified.
        for ticket in tickets:
            classification = self._classifier.classify(ticket)
            self._repository.save_ticket(TriagedTicket(ticket=ticket, classification=classification))

        groups = group_tickets(tickets, self._similarity_threshold)
        for group in groups:
            self._repository.save_group(group)
            for ticket_id in group.ticket_ids:
                self._repository.assign_group(ticket_id, group.id)

        escalations = find_escalations(tickets, self._clock(), self._escalation_days)
        for ticket, age_days in escalations:
            self._notifier.notify_escalation(ticket, age_days)

        grouped = sum(len(g.ticket_ids) for g in groups)
        summary = {
            "tickets": len(tickets),
            "groups": len(groups),
            "ungrouped": len(tickets) - grouped,
            "escalated": len(escalations),
        }
        log.info("Triage run finished: %s", summary)
        return summary
