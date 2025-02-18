import logging
import os
import typing as t
from logging.config import DictConfigurator as BaseDictConfigurator

from no_log_tears.formatter.json import JSONFormatter
from no_log_tears.formatter.soft import SoftFormatter


def is_autoload_enabled() -> bool:
    return int(os.getenv("LOGGING.AUTOLOAD", "1")) > 0


def is_debug_enabled() -> bool:
    return int(os.getenv("LOGGING.DEBUG", "0")) > 0


def is_patch_enabled() -> bool:
    return int(os.getenv("LOGGING.PATCH", "1")) > 0


class DictConfigurator(BaseDictConfigurator):
    @classmethod
    def create_default(cls) -> dict[str, object]:
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
        super().__init__(dict(config) if config else self.create_default())

    def configure(self) -> None:
        logging.captureWarnings(self.config.get("capture_warnings", False))
        super().configure()
