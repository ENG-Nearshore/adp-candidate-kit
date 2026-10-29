# Technical Assignment — AI-Powered Documentation Portal

**ESL | Candidate Technical Assignment | v2.1**
*Architecture, Agentic Engineering & Delivery Planning*
Engineering Software Lab | Engineering Group

| Positions | Deadline | Expected effort |
|---|---|---|
| AI Agentic Developer / Senior Agentic Developer | 7 calendar days | 6–8 hours |

> Markdown rendition of `assignment-v2.1.pdf`. If the two differ, the PDF is authoritative.

## 1. Business Scenario

Your engineering team has been asked to develop an internal web portal that generates technical documentation from existing software repositories using AI. Users should be able to select a repository, request documentation, and review the generated result. Behind the scenes, AI agents analyze source code and supporting information to produce an evidence-based technical conclusion.

Your task is to define the solution, plan its delivery, and demonstrate the central agentic workflow through a focused Proof of Concept (PoC). You are not expected to build the complete portal.

## 2. Assignment Scope

### A. Solution Architecture & Specification

* Describe the key functional requirements and the proposed user journey.
* Provide a high-level architecture diagram showing frontend, backend/API, agentic services, MCP integrations, and data flow.
* Explain your approach to context selection, prompt reliability, handling uncertainty, and major architecture trade-offs.

### B. Working Agentic PoC

* Demonstrate a Hub-and-Spoke multi-agent architecture: a central orchestrator delegates meaningful tasks to specialized agents, coordinates results, and maintains basic workflow state. The PoC must show actual orchestration, not merely sequential, unrelated LLM calls.
* Implement at least one working Model Context Protocol (MCP) integration to access a sample repository or relevant documentation, with defined tool schemas and basic error handling.
* Include project-level AI instructions (CLAUDE.md or equivalent) and at least one explicitly defined, reusable Agent Skill (or equivalent), demonstrably used in the workflow.
* Produce one structured Technical Conclusion describing the repository, relevant components, evidence or file references, key findings, limitations/uncertainties, and recommended next steps. Separate verified facts from assumptions.

### C. Delivery Roadmap

* Outline a realistic path from PoC to MVP and a usable internal portal: scope, prioritized milestones, main work packages, rough effort estimates and assumptions, dependencies, risks, and next steps.
* Keep the delivery plan concise and decision-oriented. You may explicitly defer features that are out of scope for the PoC.

## 3. Submission

Submit a Git repository containing the following four elements:

1. **Solution specification:** A concise requirements and architecture description with one diagram.
2. **Working PoC:** Runnable implementation, agent/MCP/skills configuration, and setup instructions.
3. **Delivery roadmap:** A compact milestone/work-package plan with estimates, assumptions, and risks.
4. **Execution evidence:** At least one sample Technical Conclusion, relevant execution trace/log, and basic validation or test evidence.

## 4. Technical Guidance & Timebox

Use the programming language, AI provider, and frameworks you consider appropriate. Claude Code, GitHub Copilot, or comparable AI-assisted tools are welcome. AI-generated source code and documentation are acceptable; you must be able to explain and defend your decisions.

Use a small sample or mock repository. A command-line PoC is sufficient. No functional frontend, production database, authentication, Kubernetes deployment, or CI/CD pipeline is required. Do not include sensitive data or live credentials. Avoid unnecessary infrastructure and excessive agent complexity.

The expected hands-on effort is approximately 6–8 hours, with seven calendar days to submit. Prioritize the complete agentic workflow and sound engineering decisions over polish or feature count. Any unfinished work should be clearly documented rather than disguised as complete.

## 5. Review & Technical Interview

We will review the architecture, demonstrated agent coordination, MCP integration, instructions and skills, reliability of the Technical Conclusion, engineering quality, and delivery reasoning. The submission will form the basis of a follow-up technical discussion. The same assignment is used across both roles, with expectations calibrated to the seniority of the position.

**What matters most:** clear thinking, meaningful orchestration, demonstrable integration, reliable outputs, and a practical route from PoC to delivery.

---

### In this kit

* An early build of the documentation portal is in `portal/`, without its documentation engine. Your PoC is that engine and plugs into the portal through the engine contract in `portal/README.md`.
* The repositories to document are listed in the portal catalog: `sample-app/` (the *Support Triage Service*, with supporting notes in `reference-docs/`) and `outage-feed/` (the *Outage Status Feed*).
* The documentation request your PoC should answer is the portal template in `documentation-request.md`.
* Setup and rules: `START_HERE.md` and `README.md`.
