"""Pydantic settings for logging configuration."""

import logging
import os
import typing as t
import warnings
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, PlainValidator
from pydantic_settings import (
    BaseSettings,
    InitSettingsSource,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)
from typing_extensions import override

from no_log_tears.config import DictConfigurator, LoggingLevelName
from no_log_tears.logger import _get_internal_logger


def _parse_logging_level(value: object) -> int:
    if isinstance(value, int):
        return value

    elif isinstance(value, str):
        value_num = logging.getLevelName(value.strip().upper())
        if not isinstance(value_num, int):
            msg = "invalid log level"
            raise TypeError(msg, value)

        return value_num

    else:
        msg = "invalid log level"
        raise TypeError(msg, value)


def _dump_logging_level(level: int) -> str:
    return logging.getLevelName(level)


LoggingLevel = t.Annotated[
    t.Union[int, LoggingLevelName],
    PlainValidator(_parse_logging_level),
    PlainSerializer(_dump_logging_level),
]

_FILE_SOURCE_BY_SUFFIX: t.Final[t.Mapping[str, t.Callable[[type[BaseSettings], Path], PydanticBaseSettingsSource]]] = {
    ".json": JsonConfigSettingsSource,
    ".yml": YamlConfigSettingsSource,
    ".yaml": YamlConfigSettingsSource,
}


class LoggingSettings(BaseSettings):
    """
    Logging configuration settings.

    It supports multiple sources of configuration: environment variables with `LOGGING__` prefix, `.env` file, and
    `.json`/`.yaml` files. Path to the file can be specified via `LOGGING__FILE` environment variable. By default, it
    tries to load `logging.json` or `logging.yaml` from the current working directory.

    The configuration is based on Python's `logging.config.dictConfig` format. For more information see
    https://docs.python.org/3/library/logging.config.html
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LOGGING__",
        env_nested_delimiter="__",
        extra="allow",
    )

    class Formatter(BaseModel):
        """Formatter settings."""

        model_config = ConfigDict(extra="allow")

        factory: t.Union[str, type[object]] = Field(alias="()")

    class Handler(BaseModel):
        """Handler settings."""

        model_config = ConfigDict(extra="allow")

        class_: t.Union[str, type[object]] = Field(alias="class")

    class RootLogger(BaseModel):
        """Root logger settings."""

        level: t.Optional[LoggingLevel] = None
        handlers: t.Optional[t.Sequence[str]] = None

    class Logger(RootLogger):
        """Logger settings."""

        propagate: t.Optional[bool] = None

    version: t.Literal[1] = 1
    incremental: bool = False
    capture_warnings: bool = True
    disable_existing_loggers: t.Optional[bool] = False
    root: t.Optional[RootLogger] = None
    loggers: t.Optional[t.Mapping[str, Logger]] = None
    handlers: t.Optional[t.Mapping[str, Handler]] = None
    formatters: t.Optional[t.Mapping[str, Formatter]] = None

    @classmethod
    @override
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customize settings sources."""
        base_sources = super().settings_customise_sources(
            settings_cls,
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

        logging_files = cls.__normalize_paths(cls.__validate_path("LOGGING__FILE")) or (
            *cls.__normalize_paths(Path.cwd() / "logging.yaml"),
            *cls.__normalize_paths(Path.cwd() / "logging.yml"),
            *cls.__normalize_paths(Path.cwd() / "logging.json"),
        )

        _get_internal_logger().info("logging files were normalized: %s", logging_files)

        return (
            base_sources
            + tuple(_FILE_SOURCE_BY_SUFFIX[file.suffix](settings_cls, file) for file in logging_files)
            + (InitSettingsSource(settings_cls, DictConfigurator.create_default()),)
        )

    def configure(self) -> None:
        """Configure logging."""
        DictConfigurator(self.model_dump(by_alias=True, exclude_none=True)).configure()

    @classmethod
    def __validate_path(cls, name: str) -> t.Optional[Path]:
        value = os.getenv(name.lower()) or os.getenv(name.upper())

        if value is None:
            return None

        path = Path(value).absolute()
        if not path.is_file():
            warnings.warn(f"config file {path} is not valid (read from {name} env)", RuntimeWarning, stacklevel=2)
            return None

        return path

    @classmethod
    def __normalize_paths(cls, path: t.Optional[Path]) -> t.Sequence[Path]:
        if path is None:
            return ()

        return path.with_stem(f"{path.stem}.override"), path
