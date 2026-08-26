"""Structured, privacy-minimized invocation logging."""

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def build_invocation_logger(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"current_sea.invocations.{log_path}")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = RotatingFileHandler(
            log_path,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    return logger


def log_invocation(logger: logging.Logger, event: dict[str, object]) -> None:
    logger.info(json.dumps(event, separators=(",", ":"), sort_keys=True))

