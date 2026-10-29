"""Group endpoints."""

from triage.api.router import Router
from triage.core.ports import TicketRepository

GROUP_ID = r"(?P<group_id>G-\d{3})"


def register(router: Router, repository: TicketRepository) -> None:
    def list_groups(params, query, body):
        return 200, repository.list_groups()

    def get_group(params, query, body):
        group = repository.get_group(params["group_id"])
        if group is None:
            return 404, {"error": "group not found"}
        tickets = [repository.get_ticket(ticket_id) for ticket_id in group.ticket_ids]
        return 200, {"group": group, "tickets": tickets}

    router.add("GET", "/groups", list_groups)
    router.add("GET", f"/groups/{GROUP_ID}", get_group)
