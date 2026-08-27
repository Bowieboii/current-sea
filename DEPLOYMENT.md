# Put CURRENT•SEA into its intended environment

The asset becomes real in its intended sense when an external AI agent can
discover and invoke it. Local calls are verification only.

## 1. Prove the release locally

```powershell
uv sync
uv run pytest
```

## 2. Deploy the application

```powershell
uv run fastapi deploy
```

The command opens FastAPI Cloud sign-in and creates the application. The free
Hobby tier is sufficient for this trial.

## 3. Attach durable telemetry

In the FastAPI Cloud application, add the Neon integration. It injects
`DATABASE_URL`; this project automatically switches from local SQLite to that
PostgreSQL database.

Set these application environment variables, replacing the example hostname:

```text
CURRENT_SEA_ALLOWED_HOSTS=your-app.fastapicloud.dev,your-app.fastapicloud.dev:*
CURRENT_SEA_ALLOWED_ORIGINS=https://your-app.fastapicloud.dev
CURRENT_SEA_LOG_MODE=stdout
CURRENT_SEA_DAILY_LIMIT=1000
```

Redeploy after saving them. The daily limit is a coarse global safety ceiling
for the trial, not per-user authentication or billing.

## 4. Verify an actual machine invocation

```powershell
uv run python scripts/verify_remote.py https://your-app.fastapicloud.dev
```

This connects as an MCP client, discovers `scan_ambiguity`, invokes it once,
and confirms that the usage source was recorded as `mcp`.

## 5. Make the surface discoverable

Copy `server.json.template` to `server.json`, replace the GitHub username and
FastAPI Cloud hostname, then authenticate and publish through the official MCP
Registry CLI:

```powershell
mcp-publisher login github
mcp-publisher publish
```

The Registry is currently in preview. It requires the remote URL to be publicly
accessible and recommends Streamable HTTP, which is what `/mcp` provides.
The public mechanism is conventional and descriptive; the project's private
metalanguage stays private.

The trial is then active: external machine calls can accumulate, `/v1/status`
exposes aggregate usage, and no submitted text is stored. Payment mechanics
remain deliberately absent until observed use justifies them.
