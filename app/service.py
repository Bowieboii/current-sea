"""One invocation path shared by REST callers and AI-agent callers."""

from time import perf_counter
from uuid import uuid4

from sqlalchemy.engine import Engine

from app.database import (
    invocation_count_since,
    record_invocation,
    utc_day_start,
    utc_now,
)
from app.scanner import ASSET_ID, ASSET_VERSION, scan_text
from app.settings import Settings
from app.telemetry import log_invocation


class InvocationLimitReached(Exception):
    pass


class InvalidAssetInput(ValueError):
    pass


class AssetService:
    def __init__(self, engine: Engine, settings: Settings, logger):
        self.engine = engine
        self.settings = settings
        self.logger = logger

    def invoke(self, text: str, source: str) -> dict[str, object]:
        if not text.strip():
            raise InvalidAssetInput("Text must contain at least one visible character.")
        if len(text) > 10_000:
            raise InvalidAssetInput("Text cannot exceed 10,000 characters.")
        if source not in {"rest", "mcp"}:
            raise InvalidAssetInput("Invocation source is not recognized.")

        used_today = invocation_count_since(self.engine, utc_day_start())
        if used_today >= self.settings.daily_invocation_limit:
            raise InvocationLimitReached(
                "The public trial has reached its global daily invocation limit."
            )

        started = perf_counter()
        request_id = str(uuid4())
        occurred_at = utc_now()
        result = scan_text(text)
        duration_ms = round((perf_counter() - started) * 1000, 3)
        remaining = max(
            0, self.settings.daily_invocation_limit - (used_today + 1)
        )

        record_invocation(
            self.engine,
            request_id=request_id,
            occurred_at=occurred_at,
            input_char_count=len(text),
            signal_count=int(result["signal_count"]),
            ambiguity_score=int(result["ambiguity_score"]),
            duration_ms=duration_ms,
            outcome="completed",
            source=source,
        )
        log_invocation(
            self.logger,
            {
                "asset_id": ASSET_ID,
                "ambiguity_score": result["ambiguity_score"],
                "duration_ms": duration_ms,
                "event": "asset.invoked",
                "input_char_count": len(text),
                "method": result["method"],
                "occurred_at": occurred_at,
                "outcome": "completed",
                "request_id": request_id,
                "signal_count": result["signal_count"],
                "source": source,
            },
        )

        return {
            "request_id": request_id,
            "asset_id": ASSET_ID,
            "asset_version": ASSET_VERSION,
            "source": source,
            "daily_limit": self.settings.daily_invocation_limit,
            "daily_remaining": remaining,
            **result,
        }

