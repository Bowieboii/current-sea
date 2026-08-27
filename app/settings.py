"""Small, explicit runtime settings with safe local defaults."""

from dataclasses import dataclass
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _resolve_path(value: str | None, default: str) -> Path:
    path = Path(value or default)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def _database_url() -> str:
    configured = os.getenv("DATABASE_URL") or os.getenv("CURRENT_SEA_DATABASE_URL")
    if not configured:
        db_path = _resolve_path(
            os.getenv("CURRENT_SEA_DB_PATH"), "data/current_sea.db"
        )
        return f"sqlite:///{db_path.as_posix()}"

    # Neon supplies a conventional PostgreSQL URL. SQLAlchemy needs the
    # explicit psycopg driver name so it never guesses the older psycopg2.
    if configured.startswith("postgresql://"):
        return configured.replace("postgresql://", "postgresql+psycopg://", 1)
    if configured.startswith("postgres://"):
        return configured.replace("postgres://", "postgresql+psycopg://", 1)
    return configured


def _csv_setting(name: str, default: str) -> tuple[str, ...]:
    return tuple(
        item.strip() for item in os.getenv(name, default).split(",") if item.strip()
    )


@dataclass(frozen=True)
class Settings:
    database_url: str
    log_path: Path
    allowed_hosts: tuple[str, ...] = (
        "localhost",
        "localhost:*",
        "127.0.0.1",
        "127.0.0.1:*",
        "testserver",
    )
    allowed_origins: tuple[str, ...] = (
        "http://localhost:*",
        "http://127.0.0.1:*",
    )
    daily_invocation_limit: int = 1_000
    log_mode: str = "file"

    @classmethod
    def from_environment(cls) -> "Settings":
        limit = max(1, int(os.getenv("CURRENT_SEA_DAILY_LIMIT", "1000")))
        log_mode = os.getenv("CURRENT_SEA_LOG_MODE", "file").strip().lower()
        if log_mode not in {"file", "stdout"}:
            raise ValueError("CURRENT_SEA_LOG_MODE must be 'file' or 'stdout'.")

        return cls(
            database_url=_database_url(),
            log_path=_resolve_path(
                os.getenv("CURRENT_SEA_LOG_PATH"), "logs/invocations.jsonl"
            ),
            allowed_hosts=_csv_setting(
                "CURRENT_SEA_ALLOWED_HOSTS",
                "localhost,localhost:*,127.0.0.1,127.0.0.1:*,testserver",
            ),
            allowed_origins=_csv_setting(
                "CURRENT_SEA_ALLOWED_ORIGINS",
                "http://localhost:*,http://127.0.0.1:*",
            ),
            daily_invocation_limit=limit,
            log_mode=log_mode,
        )

