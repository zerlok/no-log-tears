import typing as t
from pathlib import Path

import pytest
import yaml
from _pytest.monkeypatch import MonkeyPatch

from no_log_tears.config import DictConfigurator
from no_log_tears.settings import LoggingSettings

_DEFAULT_CONFIG = DictConfigurator.create_default()


@pytest.mark.parametrize(
    ("envs", "yaml_content", "expected_config"),
    [
        pytest.param(
            None,
            None,
            _DEFAULT_CONFIG,
            id="default",
        ),
        pytest.param(
            {
                "LOGGING__ROOT__LEVEL": "INFO",
            },
            None,
            {
                **_DEFAULT_CONFIG,
                "root": {"level": "INFO", "handlers": ["console"]},
            },
            id="env patch root level",
        ),
        pytest.param(
            {
                "LOGGING__FORMATTERS__SIMPLE__()": "logging.StreamHandler",
                "LOGGING__FORMATTERS__SIMPLE__FMT": "%(asctime)s %(message)s",
            },
            None,
            {
                **_DEFAULT_CONFIG,
                "formatters": {
                    **_DEFAULT_CONFIG["formatters"],  # type: ignore[dict-item]
                    "simple": {
                        "()": "logging.StreamHandler",
                        "fmt": "%(asctime)s %(message)s",
                    },
                },
            },
            id="env add simple formatter",
        ),
        pytest.param(
            {
                "LOGGING__HANDLERS__CONSOLE__FORMATTER": "verbose",
            },
            None,
            {
                **_DEFAULT_CONFIG,
                "handlers": {
                    **_DEFAULT_CONFIG["handlers"],  # type: ignore[dict-item]
                    "console": {
                        **_DEFAULT_CONFIG["handlers"]["console"],  # type: ignore[index]
                        "formatter": "verbose",
                    },
                },
            },
            id="env patch stdout handler formatter",
        ),
        pytest.param(
            None,
            {"root": {"level": "INFO"}},
            {
                **_DEFAULT_CONFIG,
                "root": {"level": "INFO", "handlers": ["console"]},
            },
            id="yaml patch root level",
        ),
        pytest.param(
            {"LOGGING__ROOT__LEVEL": "DEBUG"},
            {"root": {"level": "INFO"}},
            {
                **_DEFAULT_CONFIG,
                "root": {"level": "DEBUG", "handlers": ["console"]},
            },
            id="env=DEBUG, yaml=INFO",
        ),
    ],
)
def test_config_from_envs(patch_envs: t.Mapping[str, str], expected_config: t.Mapping[str, object]) -> None:
    settings = LoggingSettings()

    assert settings.model_dump(by_alias=True) == expected_config


@pytest.fixture
def patch_envs(
    monkeypatch: MonkeyPatch,
    envs: t.Optional[t.Mapping[str, str]],
    logging_yaml: t.Optional[Path],
) -> t.Mapping[str, str]:
    result_envs = envs or {}

    for key, value in result_envs.items():
        assert isinstance(value, str)
        monkeypatch.setenv(key, value)

    if logging_yaml is not None:
        monkeypatch.setenv("LOGGING__FILE", str(logging_yaml))

    return result_envs


@pytest.fixture
def logging_yaml(
    yaml_content: t.Optional[t.Mapping[str, object]],
    tmp_path: Path,
) -> t.Optional[Path]:
    if yaml_content is None:
        return None

    path = tmp_path / "logging.yaml"

    with path.open("w") as out:
        yaml.safe_dump(yaml_content, out)

    return path
