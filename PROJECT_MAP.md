# CURRENT•SEA — Evolving Project Map

## WHERE WE ARE

**Project:** v0.001  
**Development stage:** `3 — TRIAL`  
**Economic state:** `ACTIVE`  
**Revenue state:** No revenue exists, is owed, or is implied.

The workshop exists. One asset has moved from possibility to a working form that
reality can interact with locally.

## WHAT EXISTS

- One Python project and Git-ready repository.
- One machine-callable capability: `POST /v1/ambiguity/scan`.
- One explainable, deterministic ambiguity-scanning method.
- One SQLite asset registry containing `ambiguity-scan`.
- One invocation table that records usage without retaining submitted text.
- One rotating structured log.
- One status command for viewing the asset and its invocation count.
- Five automated tests.
- Interactive API documentation at `/docs` while the service runs.

## WHAT WE JUST LEARNED

- A digital capability can be made independently callable without paid
  infrastructure.
- Its existence, developmental stage, and usage can be recorded separately from
  economic value.
- Observability does not require retaining the content people submit.
- The private `0–7` lifecycle can remain technically ordinary and useful.
- We have not learned whether anyone needs or would pay for this asset. That
  question belongs to reality, not imagination.

## THE NEXT SMALLEST STEP

Run the project locally and invoke the asset once with a sentence from real
life. Then inspect the result and run:

```powershell
uv run python scripts/status.py
```

Only after that foothold is confirmed should we decide whether to refine this
asset, expose it in a controlled public environment, or create its first
adjacent asset.

## DECISION LEDGER

| Decision | Current choice | Why |
|---|---|---|
| Language | Python | Readable, widely supported, appropriate for small services |
| HTTP framework | FastAPI | Validation and interactive docs with little code |
| Database | SQLite | Real persistence without a server or subscription |
| Environment | uv | One command handles Python, dependencies, and lockfile |
| First asset | Ambiguity Scan | Useful, explainable, cheap, testable, and descendant-rich |
| AI dependency | None | Zero marginal model cost and fully auditable behavior |
| Data retention | Aggregate metadata only | Observe use without collecting unnecessary text |
| Deployment | Local only | Prove form before adding public infrastructure |
| Monetization | None yet | Demand and reliability must precede payment mechanics |

## PRIVATE METALANGUAGE, PUBLIC MECHANISM

The development stages `VOID → SEED → FORM → TRIAL → CURRENT → YIELD →
MULTIPLICATION → SEA` are encoded as a conventional integer enum. The first
asset is registered at `3 — TRIAL`. This is meaningful to the project without
obscuring behavior or overruling telemetry.

> Mystical internally. Empirical externally.

