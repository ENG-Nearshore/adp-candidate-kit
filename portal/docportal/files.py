"""Reads repository and documentation files for the evidence viewer."""

from pathlib import Path

from docportal.catalog import Repository

MAX_BYTES = 512_000


class FileAccessError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


def resolve_evidence_path(repo: Repository, relative: str) -> Path | None:
    """Finds `relative` under the repository root first, then under its docs roots."""
    for root in (repo.path, *repo.docs_paths):
        candidate = (root / relative).resolve()
        if candidate.is_relative_to(root) and candidate.is_file():
            return candidate
    return None


def read_file(repo: Repository, relative: str) -> dict:
    if not relative:
        raise FileAccessError(400, "Query parameter 'path' is required")
    resolved = resolve_evidence_path(repo, relative)
    if resolved is None:
        raise FileAccessError(404, f"File not found in repository or its docs: {relative}")
    if resolved.stat().st_size > MAX_BYTES:
        raise FileAccessError(413, f"File too large to display: {relative}")
    lines = resolved.read_text(encoding="utf-8", errors="replace").splitlines()
    return {"path": relative, "line_count": len(lines), "lines": lines}
