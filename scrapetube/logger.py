import os
import logging
import sys

from loguru import logger
from scrapetube.config import LOG_DIR, get_today_string

LOG_LEVEL = getattr(logging, os.environ.get("LOG_LEVEL", "DEBUG"))
JSON_LOGS = True if os.environ.get("JSON_LOGS", "0") == "1" else False


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(write_to_file: bool = True):
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(LOG_LEVEL)

    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    logger.configure(handlers=[{"sink": sys.stdout, "serialize": JSON_LOGS}])
    if write_to_file:
        log_file_path = LOG_DIR / f"metadata_{get_today_string()}.log"
        logger.add(log_file_path)
