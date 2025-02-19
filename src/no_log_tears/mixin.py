"""Mixins classes for easier logging."""

import logging
import typing as t
from functools import cached_property

from typing_extensions import override

from no_log_tears.logger import Logger


class LoggerMixin:
    """
    Provides `_logger` property for logging from the instance.

    Logger instance is cached and bound to the instance.
    Instance hex id is used as extra value `self`.
    """

    @cached_property
    def _logger(self) -> Logger:
        return Logger.get_by_instance(self, {"self": hex(id(self))})


class LoggableMixin(LoggerMixin):
    """
    Mixin for objects that can be logged.

    Implements `__str__` method that returns object representation based on current logging level of the class.
    """

    @override
    def __str__(self) -> str:
        return self._to_log(self._logger.getEffectiveLevel())

    def _to_log(self, level: int) -> str:
        """Return object representation based on logging level."""
        return (
            f"<{self.__class__.__module__}.{self.__class__.__name__} object at {hex(id(self))}>"
            if level > logging.DEBUG
            else repr(self)
        )


class LogMixin(LoggerMixin):
    """
    Mixin for objects that can log messages.

    Provides `_log` property for logging from the instance with extra values.
    `_log_extra` method can be implemented to provide extra values for logger.
    """

    @property
    def _log(self) -> Logger:
        return self._logger.with_extra(self._log_extra())

    def _log_extra(self) -> t.Optional[t.Mapping[str, object]]:
        return None
