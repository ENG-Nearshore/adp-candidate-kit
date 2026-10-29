import unittest
from datetime import date

from triage.core.grouping import cosine, group_tickets, vectorize
from triage.core.models import Ticket


def ticket(ticket_id: str, title: str, description: str) -> Ticket:
    return Ticket(ticket_id, title, description, "Normal", "Open", date(2026, 9, 1), "Residential")


class GroupingTest(unittest.TestCase):
    def test_identical_text_has_similarity_one(self):
        vector = vectorize("Smart meter readings not updating")
        self.assertAlmostEqual(cosine(vector, vector), 1.0)

    def test_near_duplicates_are_grouped(self):
        tickets = [
            ticket("LU-1", "Outage map not loading", "The outage map does not load for customers."),
            ticket("LU-2", "Outage map not loading", "The outage map does not load for customers today."),
            ticket("LU-3", "Refund request", "Customer overpaid and asks for a refund."),
        ]
        groups = group_tickets(tickets, threshold=0.82)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].id, "G-001")
        self.assertEqual(groups[0].ticket_ids, ["LU-1", "LU-2"])

    def test_single_ticket_groups_are_dropped(self):
        tickets = [
            ticket("LU-1", "Street light flickering", "Light outside number 12 flickers."),
            ticket("LU-2", "New connection quote", "Developer requests a quote."),
        ]
        self.assertEqual(group_tickets(tickets, threshold=0.82), [])


if __name__ == "__main__":
    unittest.main()
