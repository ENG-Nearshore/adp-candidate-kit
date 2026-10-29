"""Starts the documentation portal: python -m docportal.main"""

from docportal.catalog import Catalog
from docportal.config import load_settings
from docportal.engine import SubprocessEngine
from docportal.runs import RunService
from docportal.server import build_handler, serve


def main() -> None:
    settings = load_settings()
    catalog = Catalog.load(settings.catalog_path)
    engine = SubprocessEngine(settings.engine_command, settings.engine_workdir)
    runs = RunService(catalog, engine, settings.runs_dir, settings.engine_timeout_seconds, settings.max_cost_eur)
    server = serve(settings.port, build_handler(catalog, runs, engine.configured))
    status = "configured" if engine.configured else "NOT configured (set ENGINE_COMMAND)"
    print(f"Documentation portal on http://127.0.0.1:{settings.port} - engine {status}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
