"""Provides soft formatter."""

import logging
import re
import typing as t
from types import TracebackType

from typing_extensions import override

from no_log_tears.formatter import ISO8601DatetimeFormatter
from no_log_tears.formatter.traceback import TracebackFormatter, TracebackGenerator


class SoftFormatter(logging.Formatter):
    """
    Soft formatter to format log records with string interpolation.

    Uses `%(field_name)s` syntax.

    If field is missing - uses default value or `???` if default is not provided.

    If `__other__` field is present in format string - all other fields will be included in a dict under this key.

    If `exclude` is provided - these fields will be excluded from `__other__` dict.
    """

    # NOTE: ignore PLR0913, because formatter can be constructed via dict configurator.
    def __init__(  # noqa: PLR0913
        self,
        fmt: t.Optional[str] = None,
        datefmt: t.Optional[str] = None,
        validate: bool = True,  # noqa: FBT001,FBT002
        exclude: t.Union[str, t.Sequence[str], None] = None,
        defaults: t.Optional[t.Mapping[str, str]] = None,
        unknown: t.Optional[str] = None,
        traceback_tail: t.Optional[int] = None,
        traceback_generator: t.Optional[TracebackGenerator] = None,
    ) -> None:
        """SoftFormatter constructor."""
        super().__init__(
            fmt=fmt,
            datefmt=datefmt,
            validate=validate,
        )

        self.__defaults = defaults or {}
        self.__unknown = unknown or "???"

        assert isinstance(self._fmt, str)
        all_fields = set(re.findall(r"%\((?P<field>\w+)\)", self._fmt))

        self.__main_fields = all_fields - {"__other__"}
        self.__add_other = "__other__" in all_fields
        self.__non_other_fields = self.__main_fields.difference(
            [exclude] if isinstance(exclude, str) else exclude if exclude is not None else ()
        ) - {"__base__"}

        if exclude is not None and "__base__" in exclude:
            # the following fields are base fields in `logging.LogRecord`
            self.__non_other_fields.update(
                {
                    "args",
                    "asctime",
                    "created",
                    "exc_info",
                    "exc_text",
                    "filename",
                    "funcName",
                    "levelname",
                    "levelno",
                    "lineno",
                    "module",
                    "msecs",
                    "msg",
                    "name",
                    "pathname",
                    "process",
                    "processName",
                    "relativeCreated",
                    "stack_info",
                    "taskName",
                    "thread",
                    "threadName",
                }
            )

        self.__time = ISO8601DatetimeFormatter() if datefmt == "ISO8601" else None
        self.__traceback = TracebackFormatter(traceback_tail=traceback_tail, traceback_generator=traceback_generator)

    @override
    def formatTime(self, record: logging.LogRecord, datefmt: t.Optional[str] = None) -> str:
        return (
            self.__time.formatTime(record, datefmt) if self.__time is not None else super().formatTime(record, datefmt)
        )

    @override
    def formatMessage(self, record: logging.LogRecord) -> str:
        """Format log record message with string interpolation."""
        assert isinstance(self._fmt, str)

        items = {
            field: getattr(record, field, self.__defaults.get(field, self.__unknown)) for field in self.__main_fields
        }

        if self.__add_other:
            items["__other__"] = {
                field: getattr(record, field, self.__unknown)
                for field in (record.__dict__.keys() - self.__non_other_fields)
            }

        return self._fmt % items

    @override
    def formatException(
        self,
        exc_info: t.Union[
            tuple[type[BaseException], BaseException, t.Optional[TracebackType]],
            tuple[None, None, None],
            bool,
            None,
        ],
    ) -> str:
        return self.__traceback.formatException(exc_info)
