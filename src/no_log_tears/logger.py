"""Custom logger with extra values binding and logging patching."""

from __future__ import annotations

import logging
import typing as t

from typing_extensions import override

from no_log_tears.config import is_debug_enabled, is_patch_enabled
from no_log_tears.record import Record

if t.TYPE_CHECKING:
    from types import TracebackType


class Logger(
    # NOTE: can't use `logging.LoggerAdapter[logging.Logger]` - raises `TypeError: 'type' object is not subscriptable`.
    logging.LoggerAdapter,  # type: ignore[type-arg]
):
    """Extension of builtin `logging.LoggerAdapter` with extra values binding."""

    @classmethod
    def get_by_name(
        cls,
        name: t.Optional[str] = None,
        extra: t.Optional[t.Mapping[str, object]] = None,
    ) -> Logger:
        """Get appropriate logger by its name."""
        return cls(logging.getLogger(name), extra)

    @classmethod
    def get_by_type(
        cls,
        obj: type[object],
        extra: t.Optional[t.Mapping[str, object]] = None,
    ) -> Logger:
        """Get logger for provided type (use type's module name & type name)."""
        return cls.get_by_name(f"{obj.__module__}.{obj.__name__}", extra)

    @classmethod
    def get_by_instance(
        cls,
        obj: object,
        extra: t.Optional[t.Mapping[str, object]] = None,
    ) -> Logger:
        """Get logger for type of provided instance."""
        return cls.get_by_type(type(obj), extra)

    def __init__(
        self,
        logger: logging.Logger,
        extra: t.Optional[t.Mapping[str, object]] = None,
    ) -> None:
        """Logger constructor."""
        super().__init__(logger, extra or {})

    def __call__(self, **kwargs: object) -> Logger:
        """Bind extra kwargs to logger, see `with_extra` method."""
        return self.with_extra(kwargs)

    @override
    def process(self, msg: str, kwargs: t.Mapping[str, object]) -> tuple[str, t.MutableMapping[str, object]]:
        return msg, {"extra": dict(**self.extra, **kwargs) if self.extra else kwargs}

    def with_extra(self, extra: t.Optional[t.Mapping[str, object]]) -> Logger:
        """
        Bind extra values to logger.

        Returns new logger instance if non-empty extra was provided. Otherwise - returns same instance.
        """
        if not extra:
            return self

        return Logger(
            logger=self.logger,
            extra=dict(**self.extra, **extra) if self.extra else extra,
        )


get_logger = Logger.get_by_name


def _get_internal_logger() -> Logger:
    log = get_logger(__name__)

    if is_debug_enabled():
        log.setLevel(logging.DEBUG)

    return log


def patch_logging() -> None:
    """Patch builtin `logging` module."""
    if is_patch_enabled():
        logging.setLogRecordFactory(Record)

        # NOTE: with patched `logging.Logger.makeRecord` method all existing loggers will not raise `KeyError` on
        # `asctime` or `message` kwargs or extra keys.
        logging.getLoggerClass().makeRecord = _make_record  # type: ignore[assignment,method-assign]

        _get_internal_logger().debug("logging was patched")


# NOTE: ignore ARG001 and PLR0913, because this is a logging module patch.
def _make_record(  # noqa: PLR0913
    self: object,  # noqa: ARG001
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
    """
    Invoke logging log record factory directly, without extra logic.

    Allows log record factory to handle all log record creation logic.
    """
    return logging.getLogRecordFactory()(
        name, level, fn, lno, msg, args, exc_info, _func=func, _sinfo=sinfo, _extra=extra
    )
