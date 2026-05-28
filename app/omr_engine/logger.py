import logging
from rich.console import Console
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)


class Logger:
    def __init__(self, name, level=logging.NOTSET):
        self.log = logging.getLogger(name)
        self.log.setLevel(level)

    def _log(self, method, *msg, sep=" "):
        func = getattr(self.log, method)
        nmsg = [str(v) for v in msg]
        func(sep.join(nmsg), stacklevel=3)

    def debug(self, *msg, sep=" "):
        self._log("debug", *msg, sep=sep)

    def info(self, *msg, sep=" "):
        self._log("info", *msg, sep=sep)

    def warning(self, *msg, sep=" "):
        self._log("warning", *msg, sep=sep)

    def error(self, *msg, sep=" "):
        self._log("error", *msg, sep=sep)

    def critical(self, *msg, sep=" "):
        self._log("critical", *msg, sep=sep)


logger = Logger(__name__)
console = Console()
