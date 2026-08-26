"""SQLite storage for the asset registry and privacy-minimized invocation data."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from app.lifecycle import DevelopmentStage, ValueState
from app.scanner import ASSET_ID, ASSET_NAME, ASSET_VERSION


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connect(db_path: Path) -> Iterator[sqlite3.Connection]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_database(db_path: Path) -> None:
    with connect(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                description TEXT NOT NULL,
                development_stage INTEGER NOT NULL,
                development_name TEXT NOT NULL,
                value_state TEXT NOT NULL,
                generation INTEGER NOT NULL DEFAULT 0,
                parent_asset_id TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (parent_asset_id) REFERENCES assets(id)
            );

            CREATE TABLE IF NOT EXISTS invocations (
                id TEXT PRIMARY KEY,
                asset_id TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                input_char_count INTEGER NOT NULL,
                signal_count INTEGER NOT NULL,
                ambiguity_score INTEGER NOT NULL,
                duration_ms REAL NOT NULL,
                outcome TEXT NOT NULL,
                FOREIGN KEY (asset_id) REFERENCES assets(id)
            );

            CREATE INDEX IF NOT EXISTS idx_invocations_asset_time
            ON invocations(asset_id, occurred_at);
            """
        )
        connection.execute(
            """
            INSERT INTO assets (
                id, name, version, description, development_stage,
                development_name, value_state, generation, parent_asset_id,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                version = excluded.version,
                description = excluded.description,
                development_stage = excluded.development_stage,
                development_name = excluded.development_name,
                value_state = excluded.value_state
            """,
            (
                ASSET_ID,
                ASSET_NAME,
                ASSET_VERSION,
                "Flags wording that may require clarification using explainable rules.",
                int(DevelopmentStage.TRIAL),
                DevelopmentStage.TRIAL.name,
                ValueState.ACTIVE,
                0,
                None,
                utc_now(),
            ),
        )


def record_invocation(
    db_path: Path,
    *,
    request_id: str,
    occurred_at: str,
    input_char_count: int,
    signal_count: int,
    ambiguity_score: int,
    duration_ms: float,
    outcome: str,
) -> None:
    with connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO invocations (
                id, asset_id, occurred_at, input_char_count, signal_count,
                ambiguity_score, duration_ms, outcome
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                ASSET_ID,
                occurred_at,
                input_char_count,
                signal_count,
                ambiguity_score,
                duration_ms,
                outcome,
            ),
        )


def read_status(db_path: Path) -> dict[str, object]:
    with connect(db_path) as connection:
        asset = connection.execute(
            "SELECT * FROM assets WHERE id = ?", (ASSET_ID,)
        ).fetchone()
        summary = connection.execute(
            """
            SELECT
                COUNT(*) AS invocation_count,
                COALESCE(SUM(signal_count), 0) AS total_signals,
                COALESCE(AVG(duration_ms), 0) AS average_duration_ms
            FROM invocations
            WHERE asset_id = ?
            """,
            (ASSET_ID,),
        ).fetchone()

    return {
        "asset": dict(asset) if asset else None,
        "summary": dict(summary),
    }
