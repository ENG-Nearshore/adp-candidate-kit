"""Entry point: python -m triage.main"""

import logging
from http.server import ThreadingHTTPServer

from triage import __version__
from triage.api import group_routes, ticket_routes
from triage.api.router import Router, build_handler
from triage.config import load_settings
from triage.container import Container


def create_server(container: Container) -> ThreadingHTTPServer:
    router = Router()
    router.add("GET", "/health", lambda params, query, body: (200, {"status": "ok", "version": __version__}))
    ticket_routes.register(router, container.repository, container.triage_service, container.explainer)
    group_routes.register(router, container.repository)
    handler = build_handler(router, container.settings.api_token)
    return ThreadingHTTPServer(("0.0.0.0", container.settings.port), handler)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    container = Container(load_settings())
    server = create_server(container)
    logging.getLogger(__name__).info("Support Triage Service %s listening on port %s", __version__, container.settings.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
