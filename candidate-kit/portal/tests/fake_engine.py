"""Stand-in engine used by the portal tests. Usage:

    python fake_engine.py <mode> --request <run-request.json> --output <dir>

Modes: valid, invalid, no-output, crash, slow, missing-evidence.
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode")
    parser.add_argument("--request", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    output = Path(args.output)
    now = datetime.now(timezone.utc).isoformat()

    if args.mode == "crash":
        print("engine failed on purpose", file=sys.stderr)
        return 3
    if args.mode == "slow":
        time.sleep(30)
        return 0
    with open(output / "trace.jsonl", "w", encoding="utf-8") as trace:
        trace.write(json.dumps({"ts": now, "event": "started", "agent": "fake"}) + "\n")
        trace.write(json.dumps({"ts": now, "event": "finished", "agent": "fake"}) + "\n")
    if args.mode == "no-output":
        return 0

    evidence_path = "does/not/exist.txt" if args.mode == "missing-evidence" else "README.md"
    conclusion = {
        "contract_version": "1.0",
        "run_id": request["run_id"],
        "repository_id": request["repository"]["id"],
        "title": "Fake conclusion",
        "sections": [
            {"title": "Overview", "body": "Placeholder text.", "evidence": [{"path": evidence_path, "line_start": 1}]}
        ],
        "usage": {"models": ["none"], "input_tokens": 0, "output_tokens": 0, "cost_eur": 0},
    }
    if args.mode == "invalid":
        del conclusion["sections"]
        conclusion["summary"] = "not part of the contract"
    (output / "conclusion.json").write_text(json.dumps(conclusion), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
