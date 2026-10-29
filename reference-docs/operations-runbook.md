# Support Triage Service — Operations Runbook

*Larkspur Utilities · Support Engineering*

## Starting the service

```bash
cd sample-app
python -m triage.main
```

The service listens on port 8085 by default. `GET /health` can be used by monitoring without a token.

## Running a triage

Triage is started manually (or by the nightly scheduler job owned by the support desk team) with:

```bash
curl -X POST -H "X-Api-Token: <token>" http://<host>:8085/triage/run
```

Every run re-imports the full export, so results from the previous run are replaced.

## Environment variables

| Variable | Notes |
|---|---|
| `TRIAGE_PORT` | HTTP port |
| `TRIAGE_API_TOKEN` | Shared token for API clients |
| `TRIAGE_TICKETS_CSV` | Path of the export file |
| `TRIAGE_CLASSIFIER` | `keyword` locally; `llm` to use the model gateway |
| `SIMILARITY_THRESHOLD` | Grouping sensitivity |
| `ESCALATION_DAYS` | Days before an open critical ticket is escalated |
| `ESCALATION_WEBHOOK_URL` | Dispatch team webhook |

## Escalation webhook

The dispatch team receives a JSON `POST` per escalated ticket:

```json
{"event": "ticket.escalated", "ticket_id": "LU-1007", "title": "Outage map not loading", "priority": "Critical", "age_days": 12}
```

If the webhook is not configured, escalations are written to the service log only.

## Known operational notes

* Restarting the service clears all triage results; run a triage again after a restart.
