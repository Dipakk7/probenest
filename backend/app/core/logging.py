import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """Configure centralized logging for Probenest."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if setup is called multiple times
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)

    # Suppress verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


logger = logging.getLogger("probenest")
