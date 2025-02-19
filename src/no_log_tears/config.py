"""Basic configuration for logging."""

import logging
import os
import typing as t
from logging.config import DictConfigurator as BaseDictConfigurator

from typing_extensions import override

from no_log_tears.formatter.json import JSONFormatter
from no_log_tears.formatter.soft import SoftFormatter


def is_autoload_enabled() -> bool:
    """
    Flag to enable/disable load and apply logging configuration automatically (on first package import).

    Default = 1.
    """
    return int(os.getenv("LOGGING.AUTOLOAD", "1")) > 0


def is_debug_enabled() -> bool:
    """
    Flag to enable/disable extra internal logging messages.

    Default = 0.
    """
    return int(os.getenv("LOGGING.DEBUG", "0")) > 0


def is_patch_enabled() -> bool:
    """
    Flag to enable/disable builtin `logging` module patching.

    Default = 1.
    """
    return int(os.getenv("LOGGING.PATCH", "1")) > 0


class DictConfigurator(BaseDictConfigurator):
    """
    Logging configuration based on dict.

    Configures warning capturing and provides default configuration.
    """

    @classmethod
    def create_default(cls) -> dict[str, object]:
        """
        Return default configuration with predefined formatters, handlers and logging levels.

        Formatters:

            * `brief` -- simple: time, level, logger name and log message
            * `verbose` -- log base known `logging.LogRecord` fields in CSV format (separator = `|`)
            * `json` -- log all record fields to JSON

        Handlers:

            * `stdout` -- log to stdout, uses `brief` formatter by default.
            * `stderr` -- log to stderr, uses `brief` formatter by default.

        Default root logger level = WARNING; handler = stderr;
        """
        return {
            "version": 1,
            "formatters": {
                "brief": {
                    "()": f"{SoftFormatter.__module__}.{SoftFormatter.__name__}",
                    "fmt": "%(asctime)s %(levelname)-7s %(name)-50s %(message)s",
                    "traceback_tail": 100,
                },
                "verbose": {
                    "()": f"{SoftFormatter.__module__}.{SoftFormatter.__name__}",
                    "fmt": "%(asctime)s|%(levelname)s|%(process)s|%(thread)s|%(taskName)s|%(name)s|%(self)s"
                    "|%(funcName)s|%(pathname)s:%(lineno)s|%(message)s",
                    "traceback_tail": 100,
                },
                "json": {
                    "()": f"{JSONFormatter.__module__}.{JSONFormatter.__name__}",
                    "traceback_tail": 100,
                },
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "formatter": "brief",
                    "stream": "ext://sys.stdout",
                },
                "stderr": {
                    "class": "logging.StreamHandler",
                    "formatter": "brief",
                    "stream": "ext://sys.stderr",
                },
            },
            "loggers": {},
            "root": {
                "level": "WARNING",
                "handlers": ["stderr"],
            },
            "incremental": False,
            "disable_existing_loggers": False,
            "capture_warnings": True,
        }

    def __init__(self, config: t.Optional[t.Mapping[str, object]] = None) -> None:
        """Construct dict configurator."""
        super().__init__(dict(config) if config else self.create_default())

    @override
    def configure(self) -> None:
        """Apply logging configuration."""
        config: t.Mapping[str, object] = self.config  # type: ignore[attr-defined]
        logging.captureWarnings(bool(config.get("capture_warnings", False)))
        super().configure()
