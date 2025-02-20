"""Provides logging utilities & patches builtin `logging` library automatically."""

__all__ = [
    "CRITICAL",
    "DEBUG",
    "ERROR",
    "INFO",
    "WARNING",
    "LogMixin",
    "LoggableMixin",
    "Logger",
    "LoggerMixin",
    "configure_logging",
    "get_logger",
]

import logging.config
import typing as t
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING

from no_log_tears.config import DictConfigurator, is_autoload_enabled
from no_log_tears.logger import Logger, get_logger, patch_logging
from no_log_tears.mixin import LoggableMixin, LoggerMixin, LogMixin

try:
    from no_log_tears.settings import LoggingSettings

except ImportError:

    def configure_logging(
        config: t.Union[t.Mapping[str, object], logging.config.DictConfigurator, None] = None,
    ) -> None:
        """Configure logging based on provided configuration."""
        (config if isinstance(config, logging.config.DictConfigurator) else DictConfigurator(config=config)).configure()

else:
    # NOTE: ignore[misc] is used, since `Config` is imported condition.
    def configure_logging(  # type: ignore[misc]
        config: t.Union[t.Mapping[str, object], logging.config.DictConfigurator, LoggingSettings, None] = None,
    ) -> None:
        """Configure logging based on provided configuration."""
        (
            config
            if isinstance(config, LoggingSettings)
            else LoggingSettings.model_validate(
                # NOTE: logging.config.DictConfigurator has `config` dict ALWAYS.
                config.config,  # type: ignore[attr-defined]
            )
            if isinstance(config, logging.config.DictConfigurator)
            else LoggingSettings.model_validate(config)
            if config
            else LoggingSettings()
        ).configure()


patch_logging()

if is_autoload_enabled():
    configure_logging()
