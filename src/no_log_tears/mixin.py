import logging
import typing as t
from functools import cached_property

from typing_extensions import override

from no_log_tears.logger import Logger


class LoggerMixin:
    @cached_property
    def _logger(self) -> Logger:
        return Logger.get_by_instance(self, {"self": hex(id(self))})


class LoggableMixin(LoggerMixin):
    @override
    def __str__(self) -> str:
        return self._to_log(self._logger.getEffectiveLevel())

    def _to_log(self, level: int) -> str:
        return (
            f"<{self.__class__.__module__}.{self.__class__.__name__} object at {hex(id(self))}>"
            if level > logging.DEBUG
            else repr(self)
        )


class LogMixin(LoggerMixin):
    @property
    def _log(self) -> Logger:
        return self._logger.with_extra(self._log_extra())

    def _log_extra(self) -> t.Optional[t.Mapping[str, object]]:
        return None
