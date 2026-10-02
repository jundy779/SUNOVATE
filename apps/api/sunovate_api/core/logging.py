"""Structured JSON logging with a per-request correlation id."""

from __future__ import annotations

import json
import logging
from contextvars import ContextVar
from datetime import UTC, datetime

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

_RESERVED = set(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {"message"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "requestId": request_id_var.get(),
        }
        # Structured extras passed via `logger.info(..., extra={...})`.
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str) -> logging.Logger:
    logger = logging.getLogger("sunovate")
    if not any(isinstance(h.formatter, JsonFormatter) for h in logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.handlers = [handler]
    logger.setLevel(level.upper())
    logger.propagate = False
    return logger
