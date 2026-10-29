# Support Triage Service — Architecture Notes

*Larkspur Utilities · Support Engineering · last edited March 2026, before the grouping rewrite*

## Overview

The Support Triage Service reduces manual sorting work for the support desk. Each run imports the ticket export, assigns every ticket a category and urgency, groups tickets that describe the same problem, and alerts the dispatch team about critical tickets that are waiting too long.

## Components

| Component | Responsibility |
|---|---|
| HTTP API | JSON endpoints for running triage and reading tickets and groups. Protected by a shared API token. |
| Ticket import | Reads the nightly CSV export from the support desk tool. |
| Classifier | Assigns category (access, billing, metering, outage, other) and urgency. A keyword-based classifier is used locally; a model-based classifier can be enabled. |
| Grouping | Finds candidate duplicates by text similarity. Each candidate duplicate pair is then confirmed by the LLM before the tickets are merged into a group. |
| Escalation | Notifies the dispatch team when a critical ticket stays unresolved for too long. |
| Storage | Keeps the latest triage result for the API to serve. |

## Flow of a triage run

1. Import all tickets from the export.
2. Classify each ticket.
3. Group similar tickets.
4. Send escalations for stale critical tickets.
5. Return a summary (tickets, groups, ungrouped, escalated).

## Design principles

* The service never changes tickets in the support desk tool; all results stay inside the service.
* External calls (model, webhook) sit behind small interfaces so they can be replaced or stubbed in tests.
