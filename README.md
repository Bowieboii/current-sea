# CURRENT•SEA v0.001

One real, observable digital micro-asset—not a simulated business and not a
claim about future money.

This first asset accepts text and flags wording that may require clarification.
It uses transparent rules, returns reasons and clarification questions, records
that it was invoked, and does **not** store the submitted text.

## The one action to take now

Extract this project, open PowerShell inside the `CURRENT-SEA` folder, and run:

```powershell
uv sync
uv run fastapi dev app/main.py
```

If PowerShell says `uv` is not recognized, install it once with:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then close and reopen PowerShell before running the first two commands.

When the server starts, open <http://127.0.0.1:8000/docs>. Expand
`POST /v1/ambiguity/scan`, click **Try it out**, and submit:

```json
{
  "text": "We might send it soon."
}
```

That single invocation is the completion of the first personal foothold.

## What the response means

- `request_id`: a unique receipt for this invocation.
- `ambiguity_score`: a simple 0–100 heuristic score, not a truth claim.
- `signals`: the exact phrases flagged, why they may be unclear, and what to ask.
- `method`: the versioned mechanism that produced the result.
- `limitation`: the boundary of what the asset can honestly claim.

## Observe the current

With the server stopped or in a second PowerShell window, run:

```powershell
uv run python scripts/status.py
```

This reads the asset registry and invocation totals from the local SQLite
database. Runtime files appear in `data/` and `logs/`; Git ignores them.

## Verify the workshop

```powershell
uv run pytest
```

The tests verify the endpoint, the registry, observation, and the privacy rule
that raw submitted text is not retained.

## Why this stack

- **Python 3.12+** keeps the code readable and lets the project use SQLite
  without running a separate database server.
- **FastAPI** supplies request validation, a callable HTTP interface, and the
  interactive `/docs` page with little machinery.
- **uv** creates the isolated environment, installs the correct Python version
  when necessary, and locks exact dependency versions.
- **SQLite** is a real disk-backed database with no account or monthly bill.
- **pytest** gives us a repeatable way to prove behavior before changing it.

The current local cost is $0.

## What exists

```text
app/main.py         HTTP surface and invocation flow
app/scanner.py      The first useful capability
app/database.py     Asset registry and invocation records
app/lifecycle.py    Development and value-state metalanguage
app/telemetry.py    Structured, privacy-minimized logs
scripts/status.py   Human-readable observation
tests/test_api.py   Behavioral proof
PROJECT_MAP.md      Evolving position and next foothold
```

## Honest boundary

`ambiguity-scan` is a deterministic wording heuristic. It cannot understand all
context and must not be represented as legal review, fact verification, or
proof that a statement is ambiguous. It is currently an **ACTIVE** asset in
**3 — TRIAL**, not PAYABLE revenue and not validated demand.

No public deployment, payment processing, personal data collection, external AI
service, or recurring expense has been introduced in v0.001.

