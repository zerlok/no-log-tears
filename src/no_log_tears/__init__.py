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

import typing as t
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING

from no_log_tears.config import DictConfigurator, LoggingLevelOrName, is_autoload_enabled
from no_log_tears.logger import Logger, get_logger, patch_logging
from no_log_tears.mixin import LoggableMixin, LoggerMixin, LogMixin

try:
    from no_log_tears.settings import Config

except ImportError:

    def configure_logging(
        config: t.Optional[t.Mapping[str, object]] = None,
        level: t.Optional[LoggingLevelOrName] = None,
        formatter: t.Optional[str] = None,
        handler: t.Optional[str] = None,
        traceback_tail: t.Optional[int] = None,
    ) -> None:
        """Configure logging based on provided configuration."""
        DictConfigurator(
            config=config,
            formatter=formatter,
            handler=handler,
            level=level,
            traceback_tail=traceback_tail,
        ).configure()

else:
    # NOTE: ignore[misc] is used, since `Config` is imported condition.
    def configure_logging(  # type: ignore[misc]
        config: t.Optional[t.Union[t.Mapping[str, object], Config]] = None,
        level: t.Optional[LoggingLevelOrName] = None,
    ) -> None:
        """Configure logging based on provided configuration."""
        cfg = (
            Config.model_validate(config)
            if isinstance(config, t.Mapping)
            else config
            if config is not None
            else Config()
        )

        if level is not None:
            if cfg.root is not None:
                cfg.root.level = level
            else:
                cfg.root = Config.RootLogger(level=level)

        cfg.configure()


patch_logging()

if is_autoload_enabled():
    configure_logging()
