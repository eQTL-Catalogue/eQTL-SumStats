import logging
import sys
from typing import Optional


def setup_logging(log_level: Optional[str] = None) -> logging.Logger:
    """
    Configure application logging with a consistent format.

    Args:
        log_level: Optional logging level (defaults to INFO if not provided)
    """
    level = getattr(logging, log_level or "INFO")

    # Configure the root logger
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    # Silence noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)

    # Create a logger for the application
    logger = logging.getLogger("eqtl_api")
    logger.setLevel(level)

    return logger


logger = setup_logging()
