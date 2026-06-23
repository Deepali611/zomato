"""Structured logging helpers for recommendation pipeline observability."""

from __future__ import annotations

import json
import logging
import os
from typing import Any


def setup_logging(level: str | None = None) -> None:
    """Configure root logging for CLI, Streamlit, and scripts."""
    log_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    in_pytest = "PYTEST_CURRENT_TEST" in os.environ
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        force=not in_pytest,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    """Emit a single-line structured log entry (JSON payload)."""
    payload = {"event": event, **fields}
    logger.info("%s", json.dumps(payload, default=str))
