"""Basic configuration for logging."""

import logging
import os
import typing as t
from logging.config import DictConfigurator as BaseDictConfigurator

from typing_extensions import override

from no_log_tears.formatter.json import JSONFormatter
from no_log_tears.formatter.soft import SoftFormatter

LoggingLevelName = t.Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LoggingLevelOrName = t.Union[int, LoggingLevelName]


def is_autoload_enabled() -> bool:
    """
    Flag to enable/disable load and apply logging configuration automatically (on first package import).

    Default = 1.
    """
    return int(os.getenv("LOGGING__AUTOLOAD", "1")) > 0


def is_debug_enabled() -> bool:
    """
    Flag to enable/disable extra internal logging messages.

    Default = 0.
    """
    return int(os.getenv("LOGGING__DEBUG", "0")) > 0


def is_patch_enabled() -> bool:
    """
    Flag to enable/disable builtin `logging` module patching.

    Default = 1.
    """
    return int(os.getenv("LOGGING__PATCH", "1")) > 0


class DictConfigurator(BaseDictConfigurator):
    """
    Logging configuration based on dict.

    Configures warning capturing and provides default configuration.
    """

    @classmethod
    def create_default(
        cls,
        level: t.Optional[LoggingLevelOrName] = None,
        formatter: t.Optional[str] = None,
        handler: t.Optional[str] = None,
        traceback_tail: t.Optional[int] = None,
    ) -> dict[str, object]:
        """
        Return default configuration with predefined formatters, handlers and logging levels.

        A few predefined formatters and handlers are available:

        Formatters:

            * `brief` -- simple: time, level, logger name and log message
            * `verbose` -- log base known `logging.LogRecord` fields in CSV format (separator = `|`)
            * `json` -- log all record fields to JSON

        Handlers:

            * `console` -- log to stderr, uses `brief` formatter by default.

        Default configuration can be overridden by providing custom values or environment variables.

        Environment variables:

            * `LOGGING__FORMATTER` -- default formatter name, (default `brief`)
            * `LOGGING__HANDLER` -- default handler name, (default `console`)
            * `LOGGING__LEVEL` -- default root logger level, (default `WARNING`)
            * `LOGGING__TRACEBACK` -- default traceback tail length, (default `100`)
        """
        return {
            "version": 1,
            "formatters": {
                "brief": {
                    "()": f"{SoftFormatter.__module__}.{SoftFormatter.__name__}",
                    "fmt": "%(asctime)s %(levelname)-7s %(name)-50s %(message)s",
                    "traceback_tail": traceback_tail or int(os.getenv("LOGGING__TRACEBACK", "100")) or None,
                },
                "verbose": {
                    "()": f"{SoftFormatter.__module__}.{SoftFormatter.__name__}",
                    "fmt": "|".join(
                        f"%({field})s"
                        for field in (
                            "asctime",
                            "created",
                            "msecs",
                            "relativeCreated",
                            "levelname",
                            "levelno",
                            "process",
                            "processName",
                            "thread",
                            "threadName",
                            "taskName",
                            "name",
                            "module",
                            "self",
                            "funcName",
                            "pathname",
                            "lineno",
                            "filename",
                            "message",
                            "msg",
                            "args",
                            "exc_text",
                            "exc_info",
                            "stack_info",
                            "__other__",
                        )
                    ),
                    "traceback_tail": None,
                },
                "json": {
                    "()": f"{JSONFormatter.__module__}.{JSONFormatter.__name__}",
                    "traceback_tail": traceback_tail or int(os.getenv("LOGGING__TRACEBACK", "100")) or None,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": formatter or os.getenv("LOGGING__FORMATTER", "brief"),
                    "stream": "ext://sys.stderr",
                },
            },
            "loggers": {},
            "root": {
                "level": level or os.getenv("LOGGING__LEVEL", "WARNING"),
                "handlers": [handler or os.getenv("LOGGING__HANDLER", "console")],
            },
            "incremental": False,
            "disable_existing_loggers": False,
            "capture_warnings": True,
        }

    def __init__(
        self,
        config: t.Optional[t.Mapping[str, object]] = None,
        level: t.Optional[LoggingLevelOrName] = None,
        formatter: t.Optional[str] = None,
        handler: t.Optional[str] = None,
        traceback_tail: t.Optional[int] = None,
    ) -> None:
        """Construct dict configurator."""
        super().__init__(
            dict(config)
            if config
            else self.create_default(
                formatter=formatter,
                handler=handler,
                level=level,
                traceback_tail=traceback_tail,
            )
        )

    @override
    def configure(self) -> None:
        """Apply logging configuration."""
        config: t.Mapping[str, object] = self.config  # type: ignore[attr-defined]
        logging.captureWarnings(bool(config.get("capture_warnings", False)))
        super().configure()
