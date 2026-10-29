"""Starts the documentation engine as a subprocess for one run."""

import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EngineResult:
    exit_code: int | None
    timed_out: bool
    stderr_tail: str


def _unquote(arg: str) -> str:
    # Non-POSIX shlex keeps surrounding quotes, e.g. for Windows paths with spaces.
    if len(arg) > 1 and arg[0] == arg[-1] and arg[0] in "\"'":
        return arg[1:-1]
    return arg


class EngineNotConfigured(RuntimeError):
    pass


class SubprocessEngine:
    """Runs `<ENGINE_COMMAND> --request <run-request.json> --output <run dir>`."""

    def __init__(self, command: str | None, workdir: Path):
        self._command = command
        self._workdir = workdir

    @property
    def configured(self) -> bool:
        return bool(self._command)

    def run(self, request_file: Path, output_dir: Path, timeout_seconds: int) -> EngineResult:
        if not self._command:
            raise EngineNotConfigured("No documentation engine configured. Set ENGINE_COMMAND.")
        args = [_unquote(a) for a in shlex.split(self._command, posix=os.name != "nt")]
        args += ["--request", str(request_file), "--output", str(output_dir)]
        stderr_file = output_dir / "engine.stderr.log"
        with open(stderr_file, "w", encoding="utf-8") as stderr, open(
            output_dir / "engine.stdout.log", "w", encoding="utf-8"
        ) as stdout:
            try:
                completed = subprocess.run(
                    args,
                    cwd=self._workdir,
                    stdout=stdout,
                    stderr=stderr,
                    timeout=timeout_seconds,
                    check=False,
                )
                exit_code, timed_out = completed.returncode, False
            except subprocess.TimeoutExpired:
                exit_code, timed_out = None, True
            except OSError as exc:
                stderr.write(f"Could not start engine: {exc}\n")
                exit_code, timed_out = 127, False
        tail = stderr_file.read_text(encoding="utf-8", errors="replace")[-2000:]
        return EngineResult(exit_code=exit_code, timed_out=timed_out, stderr_tail=tail)
