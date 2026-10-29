"""Documentation runs: creation, queueing, execution and result checks."""

import json
import queue
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from docportal.catalog import Catalog, Repository
from docportal.engine import EngineNotConfigured, SubprocessEngine
from docportal.files import resolve_evidence_path
from docportal.validation import load_schema, validate

CONTRACT_VERSION = "1.0"
FINAL_STATUSES = ("succeeded", "failed", "invalid_output", "timed_out")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Run:
    id: str
    repository_id: str
    template_id: str
    requested_by: str
    created_at: str
    directory: Path
    status: str = "queued"
    started_at: str | None = None
    finished_at: str | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    conclusion: dict | None = None

    def summary(self) -> dict:
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "template_id": self.template_id,
            "requested_by": self.requested_by,
            "status": self.status,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }

    def detail(self) -> dict:
        return {**self.summary(), "errors": self.errors, "warnings": self.warnings, "conclusion": self.conclusion}


class RunService:
    def __init__(self, catalog: Catalog, engine: SubprocessEngine, runs_dir: Path,
                 timeout_seconds: int, max_cost_eur: float):
        self._catalog = catalog
        self._engine = engine
        self._runs_dir = runs_dir
        self._timeout = timeout_seconds
        self._max_cost = max_cost_eur
        self._runs: dict[str, Run] = {}
        self._lock = threading.Lock()
        self._queue: "queue.Queue[str]" = queue.Queue()
        self._conclusion_schema = load_schema("conclusion.schema.json")
        self._trace_schema = load_schema("trace-event.schema.json")
        threading.Thread(target=self._worker, name="run-worker", daemon=True).start()

    def create(self, repository_id: str, template_id: str, request_text: str | None, requested_by: str) -> Run:
        repo = self._catalog.repository(repository_id)
        if repo is None:
            raise KeyError(f"Unknown repository: {repository_id}")
        template = self._catalog.template(template_id)
        if template is None:
            raise KeyError(f"Unknown template: {template_id}")
        with self._lock:
            run_id = f"R-{len(self._runs) + 1:04d}"
            directory = self._runs_dir / run_id
            directory.mkdir(parents=True, exist_ok=True)
            run = Run(run_id, repo.id, template.id, requested_by, _now(), directory)
            self._runs[run_id] = run
        request = {
            "contract_version": CONTRACT_VERSION,
            "run_id": run_id,
            "created_at": run.created_at,
            "requested_by": requested_by,
            "repository": {
                "id": repo.id,
                "name": repo.name,
                "path": str(repo.path),
                "docs_paths": [str(p) for p in repo.docs_paths],
                "classification": repo.classification,
                "language": repo.language,
            },
            "request": {"template_id": template.id, "text": request_text or template.text()},
            "limits": {"max_cost_eur": self._max_cost, "timeout_seconds": self._timeout},
        }
        (directory / "run-request.json").write_text(json.dumps(request, indent=2), encoding="utf-8")
        self._queue.put(run_id)
        return run

    def get(self, run_id: str) -> Run | None:
        return self._runs.get(run_id)

    def all(self) -> list[Run]:
        return sorted(self._runs.values(), key=lambda r: r.id, reverse=True)

    def trace(self, run_id: str) -> list[dict]:
        run = self._runs.get(run_id)
        if run is None:
            raise KeyError(run_id)
        trace_file = run.directory / "trace.jsonl"
        if not trace_file.exists():
            return []
        events = []
        for line in trace_file.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip():
                try:
                    events.append(json.loads(line))
                except ValueError:
                    events.append({"event": "unparseable_line", "detail": line[:200]})
        return events

    def _worker(self) -> None:
        while True:
            run_id = self._queue.get()
            try:
                self._execute(self._runs[run_id])
            except Exception as exc:  # keep the worker alive for later runs
                self._finish(self._runs[run_id], "failed", [f"Portal error: {exc}"])

    def _execute(self, run: Run) -> None:
        run.status, run.started_at = "running", _now()
        try:
            result = self._engine.run(run.directory / "run-request.json", run.directory, self._timeout)
        except EngineNotConfigured as exc:
            self._finish(run, "failed", [str(exc)])
            return
        if result.timed_out:
            self._finish(run, "timed_out", [f"Engine did not finish within {self._timeout} s"])
            return
        if result.exit_code != 0:
            self._finish(run, "failed", [f"Engine exited with code {result.exit_code}", result.stderr_tail])
            return
        errors, warnings, conclusion = self._check_outputs(run)
        run.conclusion, run.warnings = conclusion, warnings
        self._finish(run, "invalid_output" if errors else "succeeded", errors)

    def _check_outputs(self, run: Run) -> tuple[list[str], list[str], dict | None]:
        errors: list[str] = []
        warnings: list[str] = []
        conclusion = None
        conclusion_file = run.directory / "conclusion.json"
        if not conclusion_file.exists():
            errors.append("conclusion.json was not produced")
        else:
            try:
                conclusion = json.loads(conclusion_file.read_text(encoding="utf-8"))
            except ValueError as exc:
                errors.append(f"conclusion.json is not valid JSON: {exc}")
        if conclusion is not None:
            errors += [f"conclusion: {e}" for e in validate(conclusion, self._conclusion_schema)]
            if not errors:
                if conclusion["run_id"] != run.id or conclusion["repository_id"] != run.repository_id:
                    errors.append("conclusion: run_id/repository_id do not match the run request")
                warnings += self._check_evidence(conclusion, self._catalog.repository(run.repository_id))
        trace_file = run.directory / "trace.jsonl"
        if not trace_file.exists():
            errors.append("trace.jsonl was not produced")
        else:
            for number, line in enumerate(trace_file.read_text(encoding="utf-8").splitlines(), start=1):
                if not line.strip():
                    continue
                try:
                    problems = validate(json.loads(line), self._trace_schema)
                except ValueError:
                    problems = ["not valid JSON"]
                errors += [f"trace.jsonl line {number}: {p}" for p in problems]
        return errors, warnings, conclusion

    @staticmethod
    def _check_evidence(conclusion: dict, repo: Repository) -> list[str]:
        warnings = []
        for section in conclusion["sections"]:
            for item in section.get("evidence", []):
                resolved = resolve_evidence_path(repo, item["path"])
                if resolved is None:
                    warnings.append(f"Evidence not found: {item['path']} (section '{section['title']}')")
                    continue
                line_count = len(resolved.read_text(encoding="utf-8", errors="replace").splitlines())
                if item.get("line_end", item.get("line_start", 1)) > line_count:
                    warnings.append(f"Evidence line out of range: {item['path']} has {line_count} lines")
        return warnings

    def _finish(self, run: Run, status: str, errors: list[str]) -> None:
        run.status, run.finished_at = status, _now()
        run.errors = [e for e in errors if e]
