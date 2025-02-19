"""UTC time formatter for logging module."""

import logging
import typing as t
from time import gmtime, strftime

from typing_extensions import override


class ISO8601DatetimeFormatter(logging.Formatter):
    """Formats log record creation time in ISO 8601 format and in UTC timezone."""

    @override
    def formatTime(self, record: logging.LogRecord, datefmt: t.Optional[str] = None) -> str:
        """Format log record creation time."""
        ct = strftime(datefmt or "%Y-%m-%dT%H:%M:%S", gmtime(record.created))
        msecs = f"{record.created - int(record.created):.6f}"
        return f"{ct}.{msecs[2:]}Z"
