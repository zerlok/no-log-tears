"""Provides soft formatter."""

import logging
import re
import typing as t

from typing_extensions import override

from no_log_tears.formatter.traceback import TracebackFormatter, TracebackGenerator


class SoftFormatter(TracebackFormatter):
    """
    Soft formatter to format log records with string interpolation.

    Uses `%(field_name)s` syntax.

    If field is missing - uses default value or `???` if default is not provided.
    """

    # NOTE: ignore PLR0913, because formatter can be constructed via dict configurator.
    def __init__(  # noqa: PLR0913
        self,
        fmt: t.Optional[str] = None,
        datefmt: t.Optional[str] = None,
        validate: bool = True,  # noqa: FBT001,FBT002
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
            traceback_tail=traceback_tail,
            traceback_generator=traceback_generator,
        )
        self.__defaults = defaults or {}
        self.__unknown = unknown or "???"

        assert isinstance(self._fmt, str)
        self.__fields: t.Sequence[str] = re.findall(r"%\((?P<field>\w+)\)", fmt) if fmt is not None else list[str]()

    @override
    def formatMessage(self, record: logging.LogRecord) -> str:
        """Format log record message with string interpolation."""
        assert isinstance(self._fmt, str)
        return self._fmt % {
            field: getattr(record, field, self.__defaults.get(field, self.__unknown)) for field in self.__fields
        }
