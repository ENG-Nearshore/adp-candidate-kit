# Larkspur Documentation Portal

Internal web portal where engineers pick a repository from the catalog, choose a documentation template, start a documentation run, and read the resulting **Technical Conclusion** together with the evidence it cites and a trace of how it was produced.

The portal does not generate documentation itself. Each run is handed to a **documentation engine**, an external command that the portal starts and whose output it validates and displays. This build ships **without an engine**: until `ENGINE_COMMAND` is set, every run ends as `failed` with the message "No documentation engine configured".

## Requirements

Python 3.10 or newer. No third-party packages.

## Run

```bash
cd portal
python -m docportal.main          # http://127.0.0.1:8080
```

With an engine:

```bash
# macOS / Linux
ENGINE_COMMAND="python my-engine/run.py" python -m docportal.main
# Windows PowerShell
$env:ENGINE_COMMAND = "python my-engine\run.py"; python -m docportal.main
```

The engine runs in `ENGINE_WORKDIR` (default: the repository root), so relative paths in `ENGINE_COMMAND` are resolved from there. In the examples, `my-engine/` is a top-level folder of this repository.

## Tests

```bash
python -m unittest discover -s tests -t .
```

`tests/fake_engine.py` is a stand-in engine used by the tests. It produces placeholder output only.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `PORTAL_PORT` | `8080` | HTTP port (bound to 127.0.0.1) |
| `PORTAL_CATALOG` | `catalog.json` | Repository and template catalog |
| `PORTAL_RUNS_DIR` | `runs` | Where run folders are written |
| `ENGINE_COMMAND` | unset | Command that starts the documentation engine |
| `ENGINE_WORKDIR` | repository root (parent of `portal/`) | Working directory for the engine process |
| `ENGINE_TIMEOUT_SECONDS` | `600` | Run is marked `timed_out` after this |
| `PORTAL_MAX_COST_EUR` | `0.50` | Value passed to the engine as `limits.max_cost_eur` |

Relative paths are resolved against `portal/`, except `ENGINE_WORKDIR`, which is resolved against the repository root.

## Catalog

`catalog.json` lists the repositories that can be documented (id, name, owner, language, `classification`, source path, optional documentation paths) and the request templates. The `architecture-overview` template text is read from `../documentation-request.md`.

## Engine contract (version 1.0)

The JSON schemas are in [`contract/`](contract/).

### Invocation

For each run the portal creates `runs/<run_id>/`, writes `run-request.json` into it, and starts:

```
<ENGINE_COMMAND> --request <run dir>/run-request.json --output <run dir>
```

* Working directory: `ENGINE_WORKDIR`. The engine inherits the portal's environment variables.
* Exit code `0` means the engine finished; anything else marks the run `failed` (the end of stderr is shown in the run).
* Runs are executed one at a time, in the order they were created.

### Input: `run-request.json`

| Field | Meaning |
|---|---|
| `contract_version` | `"1.0"` |
| `run_id` | e.g. `R-0001` |
| `created_at`, `requested_by` | When and by whom the run was started |
| `repository.id`, `.name`, `.language` | From the catalog |
| `repository.path` | Absolute path of the repository source |
| `repository.docs_paths` | Absolute paths of supporting documentation (may be empty) |
| `repository.classification` | `public`, `internal` or `confidential` |
| `request.template_id`, `request.text` | The template and the request text (possibly edited by the user) |
| `limits.max_cost_eur` | Model cost budget for this run |
| `limits.timeout_seconds` | Time after which the portal stops the engine |

### Output (written into the run directory)

**`conclusion.json`** (schema `conclusion.schema.json`):

* `contract_version`, `run_id`, `repository_id` (must match the request), `title`.
* `sections[]`: `title`, `body` (Markdown), optional `evidence[]` items `{path, line_start?, line_end?}` and optional `extensions` object.
* Optional `usage`: `models[]`, `input_tokens`, `output_tokens`, `cost_eur`.
* Optional top-level `extensions` object.

Evidence `path` is relative to the repository root or to one of its documentation folders. The portal links each evidence item to the file viewer and adds a warning to the run if the file or line does not exist. Properties not defined in the schema are rejected; put additional structured data in `extensions`.

**`trace.jsonl`**: one JSON object per line, required `ts` and `event`, optional `agent`, `tool`, `detail`. The portal shows the trace while the run is in progress and after it finishes.

### Run statuses

| Status | Meaning |
|---|---|
| `queued` | Waiting for the engine |
| `running` | Engine started |
| `succeeded` | Engine exited with `0` and both outputs are valid |
| `invalid_output` | Engine exited with `0` but an output is missing or does not match the schema |
| `failed` | No engine configured, engine could not start, or non-zero exit code |
| `timed_out` | Engine exceeded `ENGINE_TIMEOUT_SECONDS` |

## HTTP API

| Method and path | Purpose |
|---|---|
| `GET /health` | Portal status and whether an engine is configured |
| `GET /api/repos` | Catalog repositories |
| `GET /api/templates` | Templates, including their text |
| `POST /api/runs` | Start a run: `{"repository_id", "template_id", "request_text"?, "requested_by"?}` → `202` |
| `GET /api/runs` | All runs, newest first |
| `GET /api/runs/{id}` | Run detail with errors, warnings and conclusion |
| `GET /api/runs/{id}/trace` | Trace events |
| `GET /api/repos/{id}/file?path=` | File content for the evidence viewer (repository and documentation folders only) |

## Notes

* Local development build: it binds to 127.0.0.1 and has no sign-in.
* Runs are listed until the portal restarts; their folders stay in `runs/`.
