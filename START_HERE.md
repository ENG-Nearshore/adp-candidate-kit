# Start Here

## Your situation

Assume you work in the engineering organization of **Larkspur Utilities** (a fictional utility company). Engineering leadership wants the AI-powered documentation portal described in the assignment.

An early internal build of the portal already exists (`portal/`): engineers can pick a repository from the catalog, choose a request template, start a documentation run, and read the resulting Technical Conclusion with its cited evidence and run trace. **What it does not have is the documentation engine**, the agentic workflow that actually analyzes a repository and produces the Technical Conclusion. The portal hands each run to an external engine through a documented contract, and no engine exists yet.

* **Your PoC is that engine**, the central agentic workflow, plugged into the existing portal.
* **Your solution specification and delivery roadmap cover the portal as a whole**: what exists, what is missing, and what would have to change for it to be used across the organization.

**Support Engineering** has made the first request: an *architecture and API overview* (template `architecture-overview`) of their **Support Triage Service** (`support-triage` in the catalog). **Customer Communications** is next with the **Outage Status Feed** (`outage-feed`), and more teams will follow.

You are not building, extending, or fixing the Support Triage Service or the Outage Status Feed. They are the repositories being documented, i.e. the *input* to your workflow. The triage service's own classifier, prompts, and model gateway are things to document, not part of your solution.

## What is in this kit

| Path | What it is |
|---|---|
| `assignment-v2.1.pdf` / `assignment-v2.1.md` | The assignment (same content, two formats) |
| `README.md` | Rules for this assignment |
| `portal/` | The existing documentation portal (Python, standard library only), without an engine. Its `README.md` documents how to run it and the engine contract; JSON schemas are in `portal/contract/` |
| `documentation-request.md` | The `architecture-overview` request template; the portal sends its text to the engine |
| `sample-app/` | Catalog repository `support-triage`: the *Support Triage Service*, a fictional Python service of Larkspur's support desk (confidential) |
| `reference-docs/` | Documentation *of the Support Triage Service*, written by its team (architecture notes, operations runbook, product brief). It is input for your workflow, not a brief for what you build, and, like most real documentation, it may not be fully accurate |
| `outage-feed/` | Catalog repository `outage-feed`: the *Outage Status Feed*, a small fictional Node.js service (public) |

All data, names, hosts, and organizations in this kit are fictional.

## Where your PoC lives and how it connects

Build your PoC in this repository next to `candidate-kit/` (your commits on top of the kit commit are your history).

The portal connects to an engine **only through its engine contract** (`portal/README.md`, "Engine contract"):

* Configure your engine with `ENGINE_COMMAND`. Do not modify `portal/`. If you need to return more than the contract defines, use its `extensions` fields.
* If you believe the portal or the contract should change, that belongs in your specification and roadmap, not in a patch to `portal/`.
* The reviewer will start the portal with your `ENGINE_COMMAND` and run your engine from the portal UI. Make sure that works from a fresh clone with the instructions you provide.

## Runtimes

* **Your PoC:** any language, framework, and AI provider you consider appropriate.
* **The portal:** Python 3.10 or newer, standard library only.
* **The two repositories (optional to run):** the triage service needs Python 3.10+, the outage feed needs Node.js 18+. Neither needs to be installed, built, or deployed; they can be analyzed by reading the source alone.

```bash
cd portal
python -m unittest discover -s tests -t .     # portal tests
python -m docportal.main                      # http://127.0.0.1:8080 (no engine yet)

cd ../sample-app
python -m unittest discover -s tests -t .     # 6 tests, all passing
```

## Constraints for the portal

Set by Larkspur engineering leadership. These apply to the portal you specify and plan (solution specification and delivery roadmap). The kit is fictional, so they do not restrict which model you use for your PoC.

* Some repositories that will be documented through the portal are classified **confidential**: their source code must not be sent to model providers outside Larkspur's network.
* The budget target is **â‚¬0.50 in model cost per documentation run**, on repositories considerably larger than the ones in this kit.

## Mock / example inputs

* `portal/catalog.json`: the two catalog repositories and the request template.
* `sample-app/fixtures/tickets.csv`: 30 synthetic support tickets used by the triage service.

The triage service's optional model-backed classifier is **not** needed. Its default keyword classifier works fully offline.

## Models, providers, and costs

* Any LLM/provider/tool is permitted, including local models. State which ones you used.
* Costs are not reimbursed. Free tiers, local models, or mocked/recorded model responses are all acceptable for the PoC, provided the reviewer can run it.

## What is intentionally not provided

No documentation engine, agents, MCP servers, tool schemas, skills, or project instructions are included. Designing and building these is part of the assignment.

How you shape your multi-agent workflow (which specialised agents, how the orchestrator plans and tracks work), which MCP server(s) you build or set up and which tools they expose, and which framework or tooling you use are your decisions. There is no expected design. Explain your choices and the alternatives you considered.
