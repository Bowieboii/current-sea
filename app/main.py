"""CURRENT•SEA v0.001 HTTP application."""

from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI

from app import __version__
from app.database import initialize_database, record_invocation, utc_now
from app.lifecycle import DevelopmentStage
from app.scanner import ASSET_ID, ASSET_VERSION, scan_text
from app.schemas import HealthResponse, ScanRequest, ScanResponse
from app.settings import Settings
from app.telemetry import build_invocation_logger, log_invocation


def create_app(settings: Settings | None = None) -> FastAPI:
    runtime = settings or Settings.from_environment()
    invocation_logger = build_invocation_logger(runtime.log_path)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        initialize_database(runtime.db_path)
        yield

    app = FastAPI(
        title="CURRENT•SEA",
        summary="One observable digital economic surface.",
        description=(
            "v0.001 exposes one transparent micro-asset: an explainable scan for "
            "wording that may require clarification."
        ),
        version=__version__,
        lifespan=lifespan,
    )
    app.state.settings = runtime

    @app.get("/health", response_model=HealthResponse, tags=["workshop"])
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            project="CURRENT•SEA",
            version=__version__,
            development_stage=f"{int(DevelopmentStage.TRIAL)} — {DevelopmentStage.TRIAL.name}",
        )

    @app.post(
        "/v1/ambiguity/scan",
        response_model=ScanResponse,
        tags=["economic-surface"],
    )
    def ambiguity_scan(payload: ScanRequest) -> ScanResponse:
        started = perf_counter()
        request_id = str(uuid4())
        occurred_at = utc_now()
        result = scan_text(payload.text)
        duration_ms = round((perf_counter() - started) * 1000, 3)

        record_invocation(
            runtime.db_path,
            request_id=request_id,
            occurred_at=occurred_at,
            input_char_count=len(payload.text),
            signal_count=int(result["signal_count"]),
            ambiguity_score=int(result["ambiguity_score"]),
            duration_ms=duration_ms,
            outcome="completed",
        )
        log_invocation(
            invocation_logger,
            {
                "asset_id": ASSET_ID,
                "ambiguity_score": result["ambiguity_score"],
                "duration_ms": duration_ms,
                "event": "asset.invoked",
                "input_char_count": len(payload.text),
                "method": result["method"],
                "outcome": "completed",
                "occurred_at": occurred_at,
                "request_id": request_id,
                "signal_count": result["signal_count"],
            },
        )

        return ScanResponse(
            request_id=request_id,
            asset_id=ASSET_ID,
            asset_version=ASSET_VERSION,
            **result,
        )

    return app


app = create_app()
