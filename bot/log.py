"""Structured JSON logging to stdout and logs/bot.log.

Call style: log.info("event_name", {"field": value, ...}). The dict becomes
top-level JSON fields; the message is never %-formatted against it.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        args = record.args
        # logging only unwraps a *non-empty* single dict arg, so {} arrives as ({},)
        if isinstance(args, tuple) and len(args) == 1 and isinstance(args[0], dict):
            args = args[0]
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "msg": str(record.msg) if isinstance(args, dict) else record.getMessage(),
        }
        if isinstance(args, dict):
            payload.update(args)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def get_logger(log_dir: str = "logs", name: str = "bot") -> logging.Logger:
    """JSON logger writing to stdout and <log_dir>/<name>.log."""
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = JsonFormatter()
    handlers = (
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, f"{name}.log"), encoding="utf-8"),
    )
    for handler in handlers:
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger
