"""Groups similar tickets by comparing word-count vectors of their text."""

import math
import re
from collections import Counter

from triage.core.models import Group, Ticket

_WORD = re.compile(r"[a-z]{3,}")
_STOPWORDS = frozenset(
    "the and for with not but are was were has have had this that from when after "
    "our you your they them their its into does did can cannot again still any "
    "all also been being will would should could please since there what which".split()
)


def vectorize(text: str) -> Counter:
    return Counter(w for w in _WORD.findall(text.lower()) if w not in _STOPWORDS)


def cosine(a: Counter, b: Counter) -> float:
    dot = sum(a[w] * b[w] for w in a.keys() & b.keys())
    norm = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return dot / norm if norm else 0.0


def group_tickets(tickets: list[Ticket], threshold: float) -> list[Group]:
    """Single pass: a ticket joins the first group whose anchor ticket is at least
    `threshold` similar to it, otherwise it starts a new group. Groups that end up
    with one ticket are dropped, so that ticket stays ungrouped."""
    anchors: list[tuple[Counter, list[Ticket]]] = []
    for ticket in tickets:
        vector = vectorize(ticket.text)
        for anchor_vector, members in anchors:
            if cosine(vector, anchor_vector) >= threshold:
                members.append(ticket)
                break
        else:
            anchors.append((vector, [ticket]))

    groups: list[Group] = []
    for _, members in anchors:
        if len(members) < 2:
            continue
        group_id = f"G-{len(groups) + 1:03d}"
        groups.append(Group(id=group_id, label=_label(members), ticket_ids=[t.id for t in members]))
    return groups


def _label(members: list[Ticket]) -> str:
    counts = Counter()
    for ticket in members:
        counts.update(vectorize(ticket.title))
    return " / ".join(word for word, _ in counts.most_common(3))
