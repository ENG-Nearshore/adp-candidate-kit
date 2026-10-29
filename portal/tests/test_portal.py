import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

from docportal.catalog import Catalog
from docportal.config import PORTAL_ROOT
from docportal.engine import SubprocessEngine
from docportal.files import FileAccessError, read_file
from docportal.runs import FINAL_STATUSES, RunService
from docportal.validation import load_schema, validate

FAKE_ENGINE = Path(__file__).resolve().parent / "fake_engine.py"
CATALOG = Catalog.load(PORTAL_ROOT / "catalog.json")


def make_service(mode: str | None, runs_dir: Path, timeout: int = 20) -> RunService:
    command = f'"{sys.executable}" "{FAKE_ENGINE}" {mode}' if mode else None
    engine = SubprocessEngine(command, PORTAL_ROOT.parent)
    return RunService(CATALOG, engine, runs_dir, timeout_seconds=timeout, max_cost_eur=0.5)


def wait_for(service: RunService, run_id: str, seconds: float = 25):
    deadline = time.time() + seconds
    while time.time() < deadline:
        run = service.get(run_id)
        if run.status in FINAL_STATUSES:
            return run
        time.sleep(0.1)
    raise AssertionError(f"{run_id} did not finish")


class RunLifecycleTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.runs_dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def start(self, mode, timeout=20):
        service = make_service(mode, self.runs_dir, timeout)
        run = service.create("outage-feed", "architecture-overview", None, "tester")
        return service, wait_for(service, run.id)

    def test_run_request_matches_contract(self):
        service, run = self.start("valid")
        request = json.loads((run.directory / "run-request.json").read_text(encoding="utf-8"))
        self.assertEqual(validate(request, load_schema("run-request.schema.json")), [])
        self.assertEqual(request["repository"]["classification"], "public")
        self.assertTrue(request["request"]["text"].strip())

    def test_valid_engine_output_succeeds(self):
        _, run = self.start("valid")
        self.assertEqual(run.status, "succeeded", run.errors)
        self.assertEqual(run.warnings, [])
        self.assertEqual(run.conclusion["title"], "Fake conclusion")

    def test_trace_is_exposed(self):
        service, run = self.start("valid")
        self.assertEqual([e["event"] for e in service.trace(run.id)], ["started", "finished"])

    def test_missing_engine_fails_with_clear_message(self):
        _, run = self.start(None)
        self.assertEqual(run.status, "failed")
        self.assertIn("ENGINE_COMMAND", run.errors[0])

    def test_schema_violation_is_invalid_output(self):
        _, run = self.start("invalid")
        self.assertEqual(run.status, "invalid_output")
        self.assertTrue(any("missing 'sections'" in e for e in run.errors))
        self.assertTrue(any("unexpected property 'summary'" in e for e in run.errors))

    def test_missing_conclusion_is_invalid_output(self):
        _, run = self.start("no-output")
        self.assertEqual(run.status, "invalid_output")

    def test_engine_crash_fails(self):
        _, run = self.start("crash")
        self.assertEqual(run.status, "failed")
        self.assertIn("code 3", run.errors[0])

    def test_engine_timeout(self):
        _, run = self.start("slow", timeout=1)
        self.assertEqual(run.status, "timed_out")

    def test_unknown_evidence_is_reported(self):
        _, run = self.start("missing-evidence")
        self.assertEqual(run.status, "succeeded")
        self.assertIn("does/not/exist.txt", run.warnings[0])

    def test_unknown_repository_is_rejected(self):
        service = make_service("valid", self.runs_dir)
        with self.assertRaises(KeyError):
            service.create("nope", "architecture-overview", None, "tester")


class FileAccessTest(unittest.TestCase):
    def test_reads_repository_file(self):
        result = read_file(CATALOG.repository("outage-feed"), "README.md")
        self.assertGreater(result["line_count"], 0)

    def test_reads_docs_file(self):
        repo = CATALOG.repository("support-triage")
        result = read_file(repo, "architecture-notes.md")
        self.assertGreater(result["line_count"], 0)

    def test_rejects_path_outside_repository(self):
        repo = CATALOG.repository("outage-feed")
        for path in ("../sample-app/README.md", "..\\portal\\catalog.json", "/etc/passwd"):
            with self.assertRaises(FileAccessError) as context:
                read_file(repo, path)
            self.assertEqual(context.exception.status, 404)


if __name__ == "__main__":
    unittest.main()
