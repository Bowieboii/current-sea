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


@dataclass(frozen=True)
class Settings:
    db_path: Path
    log_path: Path

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            db_path=_resolve_path(
                os.getenv("CURRENT_SEA_DB_PATH"), "data/current_sea.db"
            ),
            log_path=_resolve_path(
                os.getenv("CURRENT_SEA_LOG_PATH"), "logs/invocations.jsonl"
            ),
        )

