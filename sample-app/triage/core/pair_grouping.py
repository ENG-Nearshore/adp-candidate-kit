"""Groups tickets by confirming candidate duplicate pairs with the model gateway.

A pair of tickets is a candidate when their word-count similarity reaches
`candidate_threshold`. Each candidate pair is then sent to the model, which
answers whether both tickets describe the same underlying problem. Confirmed
pairs are merged into groups with a union-find structure.
"""

import json
import urllib.error
import urllib.request
from collections import Counter
from typing import Protocol

from triage.core.grouping import cosine, vectorize
from triage.core.models import Group, Ticket

CONFIRM_PROMPT = (
    "You compare two utility-company support tickets. Reply with JSON only: "
    '{"same_problem": true|false, "confidence": number between 0 and 1}.'
)


class PairJudge(Protocol):
    def same_problem(self, first: Ticket, second: Ticket) -> tuple[bool, float]:
        ...


class GatewayPairJudge:
    def __init__(self, base_url: str, model: str, timeout_seconds: float = 20.0):
        self._url = base_url.rstrip("/") + "/chat/completions"
        self._model = model
        self._timeout = timeout_seconds

    def same_problem(self, first: Ticket, second: Ticket) -> tuple[bool, float]:
        payload = {
            "model": self._model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": CONFIRM_PROMPT},
                {"role": "user", "content": f"A: {first.text}\n\nB: {second.text}"},
            ],
        }
        request = urllib.request.Request(
            self._url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                body = json.load(response)
            data = json.loads(body["choices"][0]["message"]["content"])
            return bool(data["same_problem"]), float(data.get("confidence", 0.0))
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError, TypeError):
            return False, 0.0


class _UnionFind:
    def __init__(self, items: list[str]):
        self._parent = {item: item for item in items}

    def find(self, item: str) -> str:
        while self._parent[item] != item:
            self._parent[item] = self._parent[self._parent[item]]
            item = self._parent[item]
        return item

    def union(self, a: str, b: str) -> None:
        root_a, root_b = self.find(a), self.find(b)
        if root_a != root_b:
            self._parent[root_b] = root_a


def candidate_pairs(tickets: list[Ticket], candidate_threshold: float) -> list[tuple[Ticket, Ticket, float]]:
    vectors = {t.id: vectorize(t.text) for t in tickets}
    pairs = []
    for i, first in enumerate(tickets):
        for second in tickets[i + 1:]:
            score = cosine(vectors[first.id], vectors[second.id])
            if score >= candidate_threshold:
                pairs.append((first, second, score))
    pairs.sort(key=lambda p: p[2], reverse=True)
    return pairs


def group_with_confirmation(
    tickets: list[Ticket],
    judge: PairJudge,
    candidate_threshold: float = 0.75,
    min_confidence: float = 0.6,
) -> list[Group]:
    uf = _UnionFind([t.id for t in tickets])
    for first, second, _ in candidate_pairs(tickets, candidate_threshold):
        same, confidence = judge.same_problem(first, second)
        if same and confidence >= min_confidence:
            uf.union(first.id, second.id)

    clusters: dict[str, list[Ticket]] = {}
    for ticket in tickets:
        clusters.setdefault(uf.find(ticket.id), []).append(ticket)

    groups: list[Group] = []
    for members in clusters.values():
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
