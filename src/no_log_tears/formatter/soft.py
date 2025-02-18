import logging
import re
import typing as t

from typing_extensions import override

from no_log_tears.formatter.traceback import TracebackFormatter, TracebackGenerator


class SoftFormatter(TracebackFormatter):
    def __init__(
        self,
        fmt: t.Optional[str] = None,
        datefmt: t.Optional[str] = None,
        validate: bool = True,
        defaults: t.Optional[t.Mapping[str, str]] = None,
        unknown: t.Optional[str] = None,
        traceback_tail: t.Optional[int] = None,
        traceback_generator: t.Optional[TracebackGenerator] = None,
    ) -> None:
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
        assert isinstance(self._fmt, str)
        return self._fmt % {
            field: getattr(record, field, self.__defaults.get(field, self.__unknown)) for field in self.__fields
        }
