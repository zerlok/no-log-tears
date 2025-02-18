import typing as t
from pathlib import Path

import pytest
import yaml
from _pytest.monkeypatch import MonkeyPatch

from no_log_tears.config import DictConfigurator
from no_log_tears.settings import Config

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
                "LOGGING.ROOT.LEVEL": "INFO",
            },
            None,
            {
                **_DEFAULT_CONFIG,
                "root": {"level": "INFO", "handlers": ["stderr"]},
            },
            id="env patch root level",
        ),
        pytest.param(
            {
                "LOGGING.FORMATTERS.SIMPLE.()": "logging.StreamHandler",
                "LOGGING.FORMATTERS.SIMPLE.FMT": "%(asctime)s %(message)s",
            },
            None,
            {
                **_DEFAULT_CONFIG,
                "formatters": {
                    **_DEFAULT_CONFIG["formatters"],
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
                "LOGGING.HANDLERS.STDOUT.FORMATTER": "verbose",
            },
            None,
            {
                **_DEFAULT_CONFIG,
                "handlers": {
                    **_DEFAULT_CONFIG["handlers"],
                    "stdout": {**_DEFAULT_CONFIG["handlers"]["stdout"], "formatter": "verbose"},
                },
            },
            id="env patch stdout handler formatter",
        ),
        pytest.param(
            None,
            {"root": {"level": "INFO"}},
            {
                **_DEFAULT_CONFIG,
                "root": {"level": "INFO", "handlers": ["stderr"]},
            },
            id="yaml patch root level",
        ),
        pytest.param(
            {"LOGGING.ROOT.LEVEL": "DEBUG"},
            {"root": {"level": "INFO"}},
            {
                **_DEFAULT_CONFIG,
                "root": {"level": "DEBUG", "handlers": ["stderr"]},
            },
            id="env=DEBUG, yaml=INFO",
        ),
    ],
)
def test_config_from_envs(patch_envs: t.Mapping[str, str], expected_config: t.Mapping[str, object]) -> None:
    config = Config()

    assert config.model_dump(by_alias=True, exclude_none=True) == expected_config


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
        monkeypatch.setenv("LOGGING.FILE", str(logging_yaml))

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
