import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

SENSITIVE_KEYS = ("token", "admin_api_key", "authorization", "cookie", "password")


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        lowered = message.lower()
        if any(key in lowered for key in SENSITIVE_KEYS):
            record.msg = "[redacted sensitive log message]"
            record.args = ()
        return True


def configure_logging(level: str, logs_dir: Path) -> None:
    logs_dir.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    root = logging.getLogger()
    root.setLevel(level.upper())
    root.handlers.clear()

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(RedactingFilter())

    app_handler = RotatingFileHandler(
        logs_dir / "application.log",
        maxBytes=5_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    app_handler.setLevel(level.upper())
    app_handler.setFormatter(formatter)
    app_handler.addFilter(RedactingFilter())

    error_handler = RotatingFileHandler(
        logs_dir / "errors.log",
        maxBytes=5_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.addFilter(RedactingFilter())

    root.addHandler(stream_handler)
    root.addHandler(app_handler)
    root.addHandler(error_handler)

