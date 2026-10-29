"""HTTP API and static UI of the documentation portal."""

import json
import mimetypes
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from docportal.catalog import Catalog
from docportal.files import FileAccessError, read_file
from docportal.runs import RunService

STATIC_DIR = Path(__file__).resolve().parent / "static"
MAX_BODY_BYTES = 64_000

_RUN = re.compile(r"^/api/runs/(R-\d{4,})$")
_TRACE = re.compile(r"^/api/runs/(R-\d{4,})/trace$")
_FILE = re.compile(r"^/api/repos/([a-z0-9-]+)/file$")


def build_handler(catalog: Catalog, runs: RunService, engine_configured: bool):
    class Handler(BaseHTTPRequestHandler):
        server_version = "DocPortal/0.3"

        def do_GET(self):
            url = urlparse(self.path)
            route = url.path
            if route == "/health":
                return self._json(200, {"status": "ok", "engine_configured": engine_configured})
            if route == "/api/repos":
                return self._json(200, [r.summary() for r in catalog.repositories()])
            if route == "/api/templates":
                return self._json(200, [{"id": t.id, "title": t.title, "text": t.text()} for t in catalog.templates()])
            if route == "/api/runs":
                return self._json(200, [r.summary() for r in runs.all()])
            if match := _RUN.match(route):
                run = runs.get(match.group(1))
                return self._json(200, run.detail()) if run else self._error(404, "Run not found")
            if match := _TRACE.match(route):
                try:
                    return self._json(200, runs.trace(match.group(1)))
                except KeyError:
                    return self._error(404, "Run not found")
            if match := _FILE.match(route):
                repo = catalog.repository(match.group(1))
                if repo is None:
                    return self._error(404, "Repository not found")
                try:
                    path = parse_qs(url.query).get("path", [""])[0]
                    return self._json(200, read_file(repo, path))
                except FileAccessError as exc:
                    return self._error(exc.status, str(exc))
            return self._static(route)

        def do_POST(self):
            if urlparse(self.path).path != "/api/runs":
                return self._error(404, "Not found")
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY_BYTES:
                return self._error(413, "Request body too large")
            try:
                body = json.loads(self.rfile.read(length) or b"{}")
            except ValueError:
                return self._error(400, "Body must be JSON")
            if not isinstance(body, dict) or not body.get("repository_id") or not body.get("template_id"):
                return self._error(400, "repository_id and template_id are required")
            try:
                run = runs.create(
                    repository_id=body["repository_id"],
                    template_id=body["template_id"],
                    request_text=body.get("request_text"),
                    requested_by=body.get("requested_by") or "anonymous",
                )
            except KeyError as exc:
                return self._error(404, str(exc.args[0]))
            return self._json(202, run.summary())

        def _static(self, route: str):
            name = "index.html" if route in ("", "/") else route.lstrip("/")
            target = (STATIC_DIR / name).resolve()
            if not target.is_relative_to(STATIC_DIR) or not target.is_file():
                return self._error(404, "Not found")
            content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            self._send(200, target.read_bytes(), content_type)

        def _json(self, status: int, payload):
            self._send(status, json.dumps(payload).encode("utf-8"), "application/json")

        def _error(self, status: int, message: str):
            self._json(status, {"error": message})

        def _send(self, status: int, body: bytes, content_type: str):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            pass

    return Handler


def serve(port: int, handler) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), handler)
