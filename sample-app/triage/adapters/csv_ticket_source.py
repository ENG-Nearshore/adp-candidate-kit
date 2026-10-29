"""Reads tickets from the CSV export produced by the support desk tool."""

import csv
from datetime import date
from pathlib import Path

from triage.core.models import Ticket

_APP_ROOT = Path(__file__).resolve().parents[2]


class CsvTicketSource:
    def __init__(self, csv_path: str):
        path = Path(csv_path)
        self._path = path if path.is_absolute() else _APP_ROOT / path

    def load_all(self) -> list[Ticket]:
        with self._path.open(newline="", encoding="utf-8") as handle:
            return [self._to_ticket(row) for row in csv.DictReader(handle)]

    @staticmethod
    def _to_ticket(row: dict) -> Ticket:
        return Ticket(
            id=row["id"].strip(),
            title=row["title"].strip(),
            description=row["description"].strip(),
            priority=row["priority"].strip(),
            status=row["status"].strip(),
            opened_on=date.fromisoformat(row["opened_on"].strip()),
            customer_area=row["customer_area"].strip(),
        )
