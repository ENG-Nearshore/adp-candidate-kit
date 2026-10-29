import unittest
from datetime import date

from triage.core.escalation import find_escalations
from triage.core.models import Ticket

TODAY = date(2026, 10, 20)


def ticket(ticket_id: str, priority: str, status: str, opened_on: date) -> Ticket:
    return Ticket(ticket_id, "title", "description", priority, status, opened_on, "Residential")


class EscalationTest(unittest.TestCase):
    def test_stale_open_critical_ticket_is_escalated(self):
        result = find_escalations([ticket("LU-1", "Critical", "Open", date(2026, 10, 10))], TODAY, 3)
        self.assertEqual([(t.id, age) for t, age in result], [("LU-1", 10)])

    def test_ticket_exactly_at_threshold_is_not_escalated(self):
        result = find_escalations([ticket("LU-1", "Critical", "Open", date(2026, 10, 17))], TODAY, 3)
        self.assertEqual(result, [])

    def test_resolved_and_non_critical_tickets_are_ignored(self):
        tickets = [
            ticket("LU-1", "Critical", "Resolved", date(2026, 9, 1)),
            ticket("LU-2", "High", "Open", date(2026, 9, 1)),
        ]
        self.assertEqual(find_escalations(tickets, TODAY, 3), [])


if __name__ == "__main__":
    unittest.main()
