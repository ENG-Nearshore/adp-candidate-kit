# Architecture and API Overview

*Portal template `architecture-overview`. The portal sends this text to the documentation engine as the request for the selected repository.*

## Request

> Generate an **architecture and API overview** of the selected repository, so that a new engineer joining the owning team can understand what the system does, how it is built, and what to be careful about.

The result must be delivered as a structured **Technical Conclusion**.

## Expected sections

1. **Purpose and scope:** what the system does and does not do.
2. **Architecture:** main components/modules, their responsibilities and dependencies; one diagram.
3. **Entry points and API surface:** how the system starts, its endpoints, and how requests are authorized.
4. **External dependencies and configuration:** integrations and the settings that control behavior.
5. **Business rules:** the rules the system applies to the data it handles.
6. **Limitations and risks:** known weaknesses, failure behavior, and operational risks.
7. **Open questions and uncertainties:** anything that cannot be determined from the provided material.
8. **Recommended next steps.**

## Boundaries

* Treat the repository and its supporting documentation as **read-only**.
* Every factual statement must reference the file(s) it is based on (path, and line where practical).
* Clearly separate **verified facts** from **assumptions/inferences**. If something cannot be determined from the provided material, say so instead of guessing.
* External endpoints referenced by the repository are not available and do not need to be contacted.
