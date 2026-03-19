import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def _build_handler(filename: str) -> RotatingFileHandler:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    return RotatingFileHandler(
        log_dir / filename,
        maxBytes=500_000,
        backupCount=3
    )


def get_logger(name: str = "ems"):
    handler = _build_handler("ems.log")
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger


def get_audit_logger(name: str = "ems_audit"):
    handler = _build_handler("ems_audit.log")
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger
