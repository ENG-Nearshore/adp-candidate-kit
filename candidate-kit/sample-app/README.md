# Support Triage Service

Internal service of the Larkspur Utilities support desk. It imports the nightly ticket export, classifies each ticket, groups similar tickets so support staff can handle them together, and alerts the dispatch team about critical tickets that have been waiting too long.

## Requirements

Python 3.10 or newer. No third-party packages.

## Run

```bash
python -m triage.main            # listens on port 8085
```

```bash
curl http://localhost:8085/health
curl -X POST -H "X-Api-Token: local-dev-token" http://localhost:8085/triage/run
curl -H "X-Api-Token: local-dev-token" http://localhost:8085/groups
```

## Tests

```bash
python -m unittest discover -s tests -t .
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `TRIAGE_PORT` | `8085` | HTTP port |
| `TRIAGE_API_TOKEN` | `local-dev-token` | Value expected in the `X-Api-Token` header |
| `TRIAGE_TICKETS_CSV` | `fixtures/tickets.csv` | Ticket export to import |
| `TRIAGE_CLASSIFIER` | `keyword` | `keyword` or `llm` (model gateway) |
| `SIMILARITY_THRESHOLD` | `0.82` | Minimum similarity for two tickets to share a group |
| `ESCALATION_DAYS` | `3` | Age after which open critical tickets are escalated |
| `ESCALATION_WEBHOOK_URL` | unset | Dispatch team webhook; escalations are only logged when unset |

## Notes

* Storage is demo storage held in memory; every triage run starts from a fresh import.
* `fixtures/tickets.csv` contains synthetic tickets for local development.
