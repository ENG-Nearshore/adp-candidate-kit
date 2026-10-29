"""Runtime settings, read once from environment variables at startup."""

import os
from dataclasses import dataclass
from pathlib import Path

PORTAL_ROOT = Path(__file__).resolve().parent.parent
KIT_ROOT = PORTAL_ROOT.parent


@dataclass(frozen=True)
class Settings:
    port: int
    catalog_path: Path
    runs_dir: Path
    engine_command: str | None
    engine_workdir: Path
    engine_timeout_seconds: int
    max_cost_eur: float


def load_settings() -> Settings:
    return Settings(
        port=int(os.getenv("PORTAL_PORT", "8080")),
        catalog_path=_resolve(os.getenv("PORTAL_CATALOG", "catalog.json"), PORTAL_ROOT),
        runs_dir=_resolve(os.getenv("PORTAL_RUNS_DIR", "runs"), PORTAL_ROOT),
        engine_command=os.getenv("ENGINE_COMMAND") or None,
        engine_workdir=_resolve(os.getenv("ENGINE_WORKDIR", "."), KIT_ROOT),
        engine_timeout_seconds=int(os.getenv("ENGINE_TIMEOUT_SECONDS", "600")),
        max_cost_eur=float(os.getenv("PORTAL_MAX_COST_EUR", "0.50")),
    )


def _resolve(value: str, base: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (base / path).resolve()
