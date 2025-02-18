import logging
import typing as t
from time import gmtime, strftime

from typing_extensions import override


class UTCTimeFormatter(logging.Formatter):
    def __init__(
        self,
        fmt: t.Optional[str] = None,
        datefmt: t.Optional[str] = None,
        style: t.Literal["%", "{", "$"] = "%",
        validate: bool = True,
    ) -> None:
        super().__init__(fmt, datefmt, style, validate)

    @override
    def formatTime(self, record: logging.LogRecord, datefmt: t.Optional[str] = None) -> str:
        ct = strftime(datefmt or "%Y-%m-%dT%H:%M:%S", gmtime(record.created))
        msecs = f"{record.created - int(record.created):.6f}"
        return f"{ct}.{msecs[2:]}Z"
