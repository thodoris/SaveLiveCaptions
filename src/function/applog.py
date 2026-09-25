'''
Logging setup shared by the launcher and the recorder.

Under pythonw.exe there is no console: sys.stdout / sys.stderr are None and
every print() - including crash tracebacks - silently disappears. We route
both into the log file so problems in the background are diagnosable.
'''
import io
import logging
import sys
from logging.handlers import RotatingFileHandler

from function import config


class _LogWriter(io.TextIOBase):
    '''File-like object that forwards written lines to a logger.'''

    def __init__(self, logger: logging.Logger, level: int):
        self._logger = logger
        self._level = level
        self._buffer = ""

    def write(self, text: str) -> int:
        self._buffer += text
        *lines, self._buffer = self._buffer.split("\n")
        for line in lines:
            if line.strip():
                self._logger.log(self._level, line.rstrip())
        return len(text)

    def flush(self) -> None:
        if self._buffer.strip():
            self._logger.log(self._level, self._buffer.rstrip())
        self._buffer = ""


def setup_logging(name: str) -> logging.Logger:
    '''Log to logs/<name>.log (rotated at 1 MB) and to the console if there is one.'''
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)

    handlers: list[logging.Handler] = [
        RotatingFileHandler(
            config.LOG_DIR / f"{name}.log",
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
    ]
    has_console = sys.stdout is not None
    if has_console:
        handlers.append(logging.StreamHandler(sys.stdout))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,
    )

    if not has_console:
        sys.stdout = _LogWriter(logging.getLogger("stdout"), logging.INFO)
        sys.stderr = _LogWriter(logging.getLogger("stderr"), logging.ERROR)

    return logging.getLogger(name)
