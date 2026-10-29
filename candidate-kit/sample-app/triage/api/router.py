"""Minimal JSON router on top of the standard library HTTP server."""

import json
import logging
import re
from dataclasses import asdict, is_dataclass
from datetime import date
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlsplit

from triage.api.auth import is_authorized

log = logging.getLogger(__name__)


class Router:
    def __init__(self):
        self._routes: list[tuple[str, re.Pattern, callable]] = []

    def add(self, method: str, pattern: str, handler) -> None:
        self._routes.append((method, re.compile(f"^{pattern}$"), handler))

    def dispatch(self, method: str, path: str, query: dict, body: dict | None):
        path_matched = False
        for route_method, regex, handler in self._routes:
            match = regex.match(path)
            if not match:
                continue
            path_matched = True
            if route_method == method:
                return handler(match.groupdict(), query, body)
        if path_matched:
            return 405, {"error": "method not allowed"}
        return 404, {"error": "not found"}


def _default(value):
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, date):
        return value.isoformat()
    raise TypeError(f"Not serializable: {type(value).__name__}")


def build_handler(router: Router, api_token: str):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self._handle("GET")

        def do_POST(self):
            self._handle("POST")

        def _handle(self, method: str):
            url = urlsplit(self.path)
            if not is_authorized(url.path, self.headers, api_token):
                return self._send(401, {"error": "missing or invalid API token"})
            query = {k: v[0] for k, v in parse_qs(url.query).items()}
            body = None
            length = int(self.headers.get("Content-Length") or 0)
            if length:
                try:
                    body = json.loads(self.rfile.read(length))
                except ValueError:
                    return self._send(400, {"error": "invalid JSON body"})
            try:
                status, payload = router.dispatch(method, url.path, query, body)
            except Exception:
                log.exception("Unhandled error on %s %s", method, url.path)
                status, payload = 500, {"error": "internal error"}
            self._send(status, payload)

        def _send(self, status: int, payload) -> None:
            data = json.dumps(payload, default=_default).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, fmt, *args):
            log.info("%s - %s", self.address_string(), fmt % args)

    return Handler
