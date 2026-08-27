"""Portable persistence for the asset registry and invocation telemetry.

SQLite remains the zero-setup local database. The same code uses PostgreSQL
when FastAPI Cloud injects a Neon DATABASE_URL.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    func,
    inspect,
    select,
    text,
    update,
)
from sqlalchemy.engine import Engine

from app.lifecycle import DevelopmentStage, ValueState
from app.scanner import ASSET_ID, ASSET_NAME, ASSET_VERSION


metadata = MetaData()

assets = Table(
    "assets",
    metadata,
    Column("id", String(120), primary_key=True),
    Column("name", String(200), nullable=False),
    Column("version", String(40), nullable=False),
    Column("description", Text, nullable=False),
    Column("development_stage", Integer, nullable=False),
    Column("development_name", String(40), nullable=False),
    Column("value_state", String(40), nullable=False),
    Column("generation", Integer, nullable=False, default=0),
    Column("parent_asset_id", String(120), ForeignKey("assets.id")),
    Column("created_at", String(50), nullable=False),
)

invocations = Table(
    "invocations",
    metadata,
    Column("id", String(50), primary_key=True),
    Column("asset_id", String(120), ForeignKey("assets.id"), nullable=False),
    Column("occurred_at", String(50), nullable=False),
    Column("input_char_count", Integer, nullable=False),
    Column("signal_count", Integer, nullable=False),
    Column("ambiguity_score", Integer, nullable=False),
    Column("duration_ms", Float, nullable=False),
    Column("outcome", String(40), nullable=False),
    Column("source", String(20), nullable=False, default="rest"),
)

Index("idx_invocations_asset_time", invocations.c.asset_id, invocations.c.occurred_at)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def utc_day_start() -> str:
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()


def build_engine(database_url: str) -> Engine:
    connect_args = (
        {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    )
    return create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )


def initialize_database(engine: Engine) -> None:
    metadata.create_all(engine)

    # Preserve v0.001 databases instead of making the user throw them away.
    column_names = {
        column["name"] for column in inspect(engine).get_columns("invocations")
    }
    if "source" not in column_names:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE invocations "
                    "ADD COLUMN source VARCHAR(20) NOT NULL DEFAULT 'rest'"
                )
            )

    with engine.begin() as connection:
        exists = connection.execute(
            select(assets.c.id).where(assets.c.id == ASSET_ID)
        ).first()
        values = {
            "name": ASSET_NAME,
            "version": ASSET_VERSION,
            "description": (
                "Flags wording that may require clarification using explainable rules."
            ),
            "development_stage": int(DevelopmentStage.TRIAL),
            "development_name": DevelopmentStage.TRIAL.name,
            "value_state": str(ValueState.ACTIVE),
        }
        if exists:
            connection.execute(
                update(assets).where(assets.c.id == ASSET_ID).values(**values)
            )
        else:
            connection.execute(
                assets.insert().values(
                    id=ASSET_ID,
                    generation=0,
                    parent_asset_id=None,
                    created_at=utc_now(),
                    **values,
                )
            )


def invocation_count_since(engine: Engine, occurred_after: str) -> int:
    with engine.connect() as connection:
        value = connection.scalar(
            select(func.count())
            .select_from(invocations)
            .where(invocations.c.occurred_at >= occurred_after)
        )
    return int(value or 0)


def record_invocation(
    engine: Engine,
    *,
    request_id: str,
    occurred_at: str,
    input_char_count: int,
    signal_count: int,
    ambiguity_score: int,
    duration_ms: float,
    outcome: str,
    source: str,
) -> None:
    with engine.begin() as connection:
        connection.execute(
            invocations.insert().values(
                id=request_id,
                asset_id=ASSET_ID,
                occurred_at=occurred_at,
                input_char_count=input_char_count,
                signal_count=signal_count,
                ambiguity_score=ambiguity_score,
                duration_ms=duration_ms,
                outcome=outcome,
                source=source,
            )
        )


def read_status(engine: Engine) -> dict[str, object]:
    with engine.connect() as connection:
        asset_row = connection.execute(
            select(assets).where(assets.c.id == ASSET_ID)
        ).mappings().first()
        summary_row = connection.execute(
            select(
                func.count().label("invocation_count"),
                func.coalesce(func.sum(invocations.c.signal_count), 0).label(
                    "total_signals"
                ),
                func.coalesce(func.avg(invocations.c.duration_ms), 0).label(
                    "average_duration_ms"
                ),
            ).where(invocations.c.asset_id == ASSET_ID)
        ).mappings().one()
        source_rows = connection.execute(
            select(invocations.c.source, func.count().label("count"))
            .where(invocations.c.asset_id == ASSET_ID)
            .group_by(invocations.c.source)
        ).mappings()
        by_source = {
            str(row["source"]): int(row["count"]) for row in source_rows
        }

    return {
        "asset": dict(asset_row) if asset_row else None,
        "summary": {
            "invocation_count": int(summary_row["invocation_count"] or 0),
            "total_signals": int(summary_row["total_signals"] or 0),
            "average_duration_ms": float(
                summary_row["average_duration_ms"] or 0
            ),
            "by_source": by_source,
        },
    }
