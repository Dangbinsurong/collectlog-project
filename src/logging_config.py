"""Logging setup for CollectLog."""

import logging


def setup_logging(log_file):
    """Configure logging to file and return logger instance."""
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        encoding="utf-8",
    )
    return logging.getLogger("collectlog")
