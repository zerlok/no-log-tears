from __future__ import annotations

import logging
import typing as t
from functools import cache
from types import TracebackType

from no_log_tears.config import is_debug_enabled, is_patch_enabled
from no_log_tears.record import Record


class Logger(logging.LoggerAdapter):
    @classmethod
    def get_by_name(
        cls,
        name: t.Optional[str] = None,
        extra: t.Optional[t.Mapping[str, object]] = None,
    ) -> Logger:
        return cls(logging.getLogger(name), extra)

    @classmethod
    def get_by_type(
        cls,
        obj: type[object],
        extra: t.Optional[t.Mapping[str, object]] = None,
    ) -> Logger:
        return cls.get_by_name(f"{obj.__module__}.{obj.__name__}", extra)

    @classmethod
    def get_by_instance(
        cls,
        obj: object,
        extra: t.Optional[t.Mapping[str, object]] = None,
    ) -> Logger:
        return cls.get_by_type(type(obj), extra)

    def __init__(
        self,
        logger: logging.Logger,
        extra: t.Optional[t.Mapping[str, object]] = None,
    ) -> None:
        super().__init__(logger, extra or {})

    def __call__(self, **kwargs: object) -> Logger:
        return self.with_extra(kwargs)

    def process(self, msg: str, kwargs: t.Mapping[str, object]) -> tuple[str, t.MutableMapping[str, object]]:
        return msg, {"extra": dict(**self.extra, **kwargs)}

    def with_extra(self, extra: t.Optional[t.Mapping[str, object]]) -> Logger:
        if not extra:
            return self

        return Logger(
            logger=self.logger,
            extra=dict(**self.extra, **(extra or {})),
        )


get_logger = Logger.get_by_name


@cache
def get_internal_logger() -> Logger:
    log = get_logger(__name__)

    if is_debug_enabled():
        log.setLevel(logging.DEBUG)

    return log


def patch_logging() -> None:
    if is_patch_enabled():
        logging.setLogRecordFactory(Record)
        logging.getLoggerClass().makeRecord = _make_record

        log = get_internal_logger()
        log.debug("logging was patched")


def _make_record(
    self: object,
    name: str,
    level: int,
    fn: str,
    lno: int,
    msg: object,
    args: tuple[object, ...],
    exc_info: t.Union[tuple[type[BaseException], BaseException, TracebackType], tuple[None, None, None], bool, None],
    func: t.Optional[str],
    extra: t.Optional[t.Mapping[str, object]],
    sinfo: t.Optional[str],
) -> logging.LogRecord:
    return logging.getLogRecordFactory()(
        name, level, fn, lno, msg, args, exc_info, _func=func, _sinfo=sinfo, _extra=extra
    )
