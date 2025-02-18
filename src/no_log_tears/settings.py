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

from no_log_tears.config import DictConfigurator
from no_log_tears.logger import get_internal_logger


def _parse_logging_level(value: object) -> int:
    if isinstance(value, int):
        return value

    elif isinstance(value, str):
        return logging.getLevelName(value.strip().upper())

    else:
        msg = "invalid log level"
        raise TypeError(msg, value)


def _dump_logging_level(level: int) -> str:
    return logging.getLevelName(level)


LoggingLevel = t.Annotated[
    t.Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    PlainValidator(_parse_logging_level),
    PlainSerializer(_dump_logging_level),
]

_FILE_SOURCE_BY_SUFFIX: t.Final[t.Mapping[str, type[PydanticBaseSettingsSource]]] = {
    ".json": JsonConfigSettingsSource,
    ".yml": YamlConfigSettingsSource,
    ".yaml": YamlConfigSettingsSource,
}


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="logging.",
        env_nested_delimiter=".",
    )

    class Formatter(BaseModel):
        model_config = ConfigDict(extra="allow")

        factory: t.Union[str, type[object]] = Field(alias="()")

    class Handler(BaseModel):
        model_config = ConfigDict(extra="allow")

        class_: t.Union[str, type[object]] = Field(alias="class")

    class RootLogger(BaseModel):
        level: t.Optional[LoggingLevel] = None
        handlers: t.Optional[t.Sequence[str]] = None

    class Logger(RootLogger):
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
        base_sources = super().settings_customise_sources(
            settings_cls,
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

        logging_files = cls.__normalize_paths(cls.__validate_path("logging.file")) or (
            *cls.__normalize_paths(Path.cwd() / "logging.yaml"),
            *cls.__normalize_paths(Path.cwd() / "logging.json"),
        )

        get_internal_logger().debug("logging files were normalized", logging_files=logging_files)

        return (
            base_sources
            + tuple(_FILE_SOURCE_BY_SUFFIX[file.suffix](settings_cls, file) for file in logging_files)
            + (InitSettingsSource(settings_cls, DictConfigurator.create_default()),)
        )

    def configure(self) -> None:
        DictConfigurator(self.model_dump(by_alias=True, exclude_none=True)).configure()

    @classmethod
    def __validate_path(cls, name: str) -> t.Optional[Path]:
        value = os.getenv(name.lower()) or os.getenv(name.upper())

        if value is None:
            return None

        path = Path(value).absolute()
        if not path.is_file():
            warnings.warn(f"config file {path} is not valid (read from {name} env)", RuntimeWarning, stacklevel=1)
            return None

        return path

    @classmethod
    def __normalize_paths(cls, path: t.Optional[Path]) -> t.Sequence[Path]:
        if path is None:
            return ()

        return path.with_stem(f"{path.stem}.override"), path
