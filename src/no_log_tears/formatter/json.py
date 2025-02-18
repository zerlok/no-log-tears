import json
import logging
import typing as t
from datetime import date, datetime, time, timedelta
from functools import singledispatchmethod

from typing_extensions import override

from no_log_tears.formatter.traceback import TracebackFormatter, TracebackGenerator
from no_log_tears.formatter.utc import UTCTimeFormatter


class JSONFormatter(TracebackFormatter):
    def __init__(
        self,
        encoder: t.Optional[json.JSONEncoder] = None,
        traceback_tail: t.Optional[int] = None,
        traceback_generator: t.Optional[TracebackGenerator] = None,
    ) -> None:
        super().__init__()
        self.__encoder = (
            encoder
            if encoder is not None
            else json.JSONEncoder(check_circular=False, separators=(",", ":"), default=self.__encode_default)
        )
        self.__time = UTCTimeFormatter()
        self.__traceback = TracebackFormatter(traceback_tail=traceback_tail, traceback_generator=traceback_generator)

    @override
    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "asctime"):
            record.asctime = self.__time.formatTime(record)

        if not hasattr(record, "exc_text") and getattr(record, "exc_info", None):
            record.exc_text = self.__traceback.formatException(record.exc_info)

        return self.__encoder.encode(record.__dict__)

    @singledispatchmethod
    def __encode_default(self, obj: object) -> object:
        return str(obj)

    @__encode_default.register
    def __encode_date(self, obj: date) -> str:
        return obj.isoformat()

    @__encode_default.register
    def __encode_time(self, obj: time) -> str:
        return obj.isoformat()

    @__encode_default.register
    def __encode_datetime(self, obj: datetime) -> str:
        return obj.isoformat()

    @__encode_default.register
    def __encode_timedelta(self, obj: timedelta) -> str:
        return str(obj)

    @__encode_default.register(tuple)
    @__encode_default.register(set)
    @__encode_default.register(frozenset)
    def __encode_iterable(self, obj: t.Iterable[object]) -> list[object]:
        return list(obj)
