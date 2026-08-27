"""CURRENT•SEA v0.002: one service, two machine-callable doorways."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from mcp.server.transport_security import TransportSecuritySettings

from app import __version__
from app.database import build_engine, initialize_database, read_status
from app.lifecycle import DevelopmentStage
from app.mcp_server import build_mcp_server
from app.schemas import HealthResponse, ScanRequest, ScanResponse
from app.service import AssetService, InvalidAssetInput, InvocationLimitReached
from app.settings import Settings
from app.telemetry import build_invocation_logger


def create_app(settings: Settings | None = None) -> FastAPI:
    runtime = settings or Settings.from_environment()
    engine = build_engine(runtime.database_url)
    invocation_logger = build_invocation_logger(runtime.log_path, runtime.log_mode)
    service = AssetService(engine, runtime, invocation_logger)
    mcp_server = build_mcp_server(service)
    mcp_app = mcp_server.streamable_http_app(
        transport_security=TransportSecuritySettings(
            allowed_hosts=list(runtime.allowed_hosts),
            allowed_origins=list(runtime.allowed_origins),
        )
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        initialize_database(engine)
        async with mcp_server.session_manager.run():
            yield
        engine.dispose()

    app = FastAPI(
        title="CURRENT•SEA",
        summary="One observable digital economic surface.",
        description=(
            "v0.002 exposes one transparent micro-asset over REST and remote MCP: "
            "an explainable scan for wording that may require clarification."
        ),
        version=__version__,
        lifespan=lifespan,
    )
    app.state.settings = runtime
    app.state.engine = engine
    app.state.asset_service = service
    app.state.mcp_server = mcp_server

    @app.get("/health", response_model=HealthResponse, tags=["operations"])
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
        try:
            result = service.invoke(payload.text, source="rest")
        except InvalidAssetInput as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        except InvocationLimitReached as error:
            raise HTTPException(status_code=429, detail=str(error)) from error
        return ScanResponse(**result)

    @app.get("/v1/status", tags=["observation"])
    def status() -> dict[str, object]:
        """Return aggregate usage only; submitted text is never retained."""
        return read_status(engine)

    # The SDK's Streamable HTTP application serves the remote MCP endpoint at
    # /mcp. Mount last so the named FastAPI routes above retain precedence.
    app.mount("/", mcp_app)

    return app


app = create_app()
