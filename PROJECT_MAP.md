# CURRENT•SEA — Evolving Project Map

## WHERE WE ARE

**Project:** v0.002
**Development stage:** `3 — TRIAL`  
**Economic state:** `ACTIVE`  
**Revenue state:** No revenue exists, is owed, or is implied.

The asset has a deployment contract and a machine-native entrance. It remains
in TRIAL until an external agent invokes the deployed endpoint.

## WHAT EXISTS

- One Python project and Git-ready repository.
- One capability exposed through REST and remote MCP.
- One explainable, deterministic ambiguity-scanning method.
- One portable SQLite/PostgreSQL asset registry containing `ambiguity-scan`.
- One invocation table that records usage without retaining submitted text.
- One rotating structured log.
- One status command for viewing the asset and its invocation count.
- Automated proof for both machine surfaces, privacy, migration, and limits.
- A controlled free-tier deployment path and MCP Registry manifest template.

## WHAT WE JUST LEARNED

- A digital capability can be made independently callable without paid
  infrastructure.
- Its existence, developmental stage, and usage can be recorded separately from
  economic value.
- Observability does not require retaining the content people submit.
- The private `0–7` lifecycle can remain technically ordinary and useful.
- A local callable surface is not enough; discoverable external machine access
  is the next empirical threshold.
- We have not learned whether anyone needs or would pay for this asset. That
  question belongs to reality, not imagination.

## THE NEXT SMALLEST STEP

Deploy the service, attach durable telemetry, verify one remote MCP invocation,
and publish the endpoint to the MCP Registry. Start with:

```powershell
uv run fastapi deploy
```

After that foothold is confirmed, wait for external machine use before adding
payment mechanics or creating adjacent assets.

## DECISION LEDGER

| Decision | Current choice | Why |
|---|---|---|
| Language | Python | Readable, widely supported, appropriate for small services |
| HTTP framework | FastAPI | Validation and interactive docs with little code |
| Database | SQLite locally, Neon PostgreSQL remotely | Durable telemetry without an initial bill |
| Environment | uv | One command handles Python, dependencies, and lockfile |
| First asset | Ambiguity Scan | Useful, explainable, cheap, testable, and descendant-rich |
| AI dependency | None | Zero marginal model cost and fully auditable behavior |
| Data retention | Aggregate metadata only | Observe use without collecting unnecessary text |
| Deployment | FastAPI Cloud free tier | Public HTTPS, native framework path, controlled cost |
| Agent protocol | Remote MCP | Direct machine discovery and invocation |
| Public discovery | MCP Registry | Quiet technical discoverability without personal promotion |
| Monetization | None yet | Demand and reliability must precede payment mechanics |

## PRIVATE METALANGUAGE, PUBLIC MECHANISM

The development stages `VOID → SEED → FORM → TRIAL → CURRENT → YIELD →
MULTIPLICATION → SEA` are encoded as a conventional integer enum. The first
asset is registered at `3 — TRIAL`. This is meaningful to the project without
obscuring behavior or overruling telemetry.

> Mystical internally. Empirical externally.
