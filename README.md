# CURRENT•SEA v0.002

One externally deployable, machine-native digital micro-asset—not a writing
exercise, a simulated business, or a claim about future money.

This first asset accepts text and flags wording that may require clarification.
It uses transparent rules, returns reasons and clarification questions, records
that it was invoked, and does **not** store the submitted text.

## Its intended use

AI agents call `scan_ambiguity` over remote MCP when they need a cheap,
deterministic check for vague wording. REST remains available for ordinary
software clients. Both doorways record privacy-minimized usage telemetry and
never retain submitted text.

The activation sequence is:

1. Deploy the service.
2. Attach the free Neon database integration.
3. Verify a real remote MCP invocation.
4. Publish the endpoint to the official MCP Registry.
5. Observe whether external machine use accumulates.

The exact procedure is in [DEPLOYMENT.md](DEPLOYMENT.md). The first human action
inside the extracted project is:

```powershell
uv run fastapi deploy
```

## Machine surfaces

- Remote MCP: `/mcp`, tool `scan_ambiguity`
- REST: `POST /v1/ambiguity/scan`
- Aggregate observation: `GET /v1/status`
- Operational health: `GET /health`

## Observe the current

With the server stopped or in a second PowerShell window, run:

```powershell
uv run python scripts/status.py
```

This reads the asset registry and invocation totals by source. Locally it uses
SQLite; in deployment the same command can use PostgreSQL through `DATABASE_URL`.

## Verify the workshop

```powershell
uv run pytest
```

The tests verify REST and MCP invocation, migration, the global safety ceiling,
the registry, telemetry, and the privacy rule that raw text is not retained.

## Why this stack

- **Python 3.12+** keeps the code readable and lets the project use SQLite
  without running a separate database server.
- **FastAPI** supplies request validation, a callable HTTP interface, and the
  interactive `/docs` page with little machinery.
- **uv** creates the isolated environment, installs the correct Python version
  when necessary, and locks exact dependency versions.
- **SQLite / PostgreSQL** provide zero-setup local work and durable cloud telemetry.
- **MCP** makes the asset directly discoverable and callable by AI agents.
- **pytest** gives us a repeatable way to prove behavior before changing it.

The selected trial path uses free tiers and has no model inference cost.

## What exists

```text
app/main.py         REST surface and mounted remote MCP application
app/scanner.py      The first useful capability
app/service.py      One invocation path shared by REST and MCP
app/mcp_server.py   Agent-facing tool definition
app/database.py     Portable asset registry and invocation records
app/lifecycle.py    Development and value-state metalanguage
app/telemetry.py    Structured, privacy-minimized logs
scripts/status.py   Human-readable observation
scripts/verify_remote.py  Deployment verification from an MCP client
DEPLOYMENT.md       Controlled activation path
PROJECT_MAP.md      Evolving position and next foothold
```

## Honest boundary

`ambiguity-scan` is a deterministic wording heuristic. It cannot understand all
context and must not be represented as legal review, fact verification, or
proof that a statement is ambiguous. It is currently an **ACTIVE** asset in
**3 — TRIAL**, not PAYABLE revenue and not validated demand.

v0.002 is deployment-ready but is not publicly live until its owner completes
FastAPI Cloud authentication and deployment. It has no payment processing,
external model dependency, or recurring expense. The trial limit is global and
coarse; billing and per-client authentication belong to a later stage only if
observed external use warrants them.
