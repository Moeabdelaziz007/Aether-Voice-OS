import logging
import sys
from pathlib import Path
from typing import Optional

import structlog


def configure_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Configure structured logging for Aether.

    Sets up both a human-readable console logger and an optional
    machine-readable JSON file logger.
    """
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    console_renderer = structlog.dev.ConsoleRenderer(
        colors=True,
        exception_formatter=structlog.dev.plain_traceback,
    )

    file_renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=console_renderer,
            foreign_pre_chain=shared_processors,
        )
    )

    handlers = [console_handler]

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=file_renderer,
                foreign_pre_chain=shared_processors,
            )
        )
        handlers.append(file_handler)

    root_logger = logging.getLogger()

    # Safely get log level, default to INFO if invalid
    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates, then add ours
    root_logger.handlers = []
    for handler in handlers:
        root_logger.addHandler(handler)

    return structlog.get_logger()
