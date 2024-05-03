import logging
from enum import IntEnum
from pathlib import Path
from typing import Optional

LOG_FORMAT = "%(asctime)s %(name)s:%(funcName)s:%(lineno)s [%(levelname)s]: %(message)s"


class LogLevel(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


def init_logging(
    log_level: LogLevel = LogLevel.INFO,
    log_file: Optional[Path] = None,
    overwrite: bool = False,
) -> None:
    logging.basicConfig(
        filename=log_file,
        filemode="w" if overwrite else "a",
        format=LOG_FORMAT,
        encoding="utf-8",
        level=log_level,
    )
