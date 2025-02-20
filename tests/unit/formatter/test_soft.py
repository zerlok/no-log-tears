import typing as t

import pytest

from no_log_tears.formatter.soft import SoftFormatter
from no_log_tears.record import Record


@pytest.mark.parametrize(
    ("fmt", "exclude", "record_msg", "record_extra", "expected_str"),
    [
        pytest.param(
            "%(message)s",
            None,
            "hello",
            {},
            "hello",
        ),
        pytest.param(
            "%(asctime)s %(levelname)s %(message)s",
            None,
            "this is log",
            {},
            "2025-01-02 03:04:05,123 INFO this is log",
        ),
        pytest.param(
            "%(asctime)s %(message)s %(__other__)s",
            "__base__",
            "this is log",
            {},
            "2025-01-02 03:04:05,123 this is log {}",
        ),
        pytest.param(
            "%(asctime)s %(message)s %(__other__)s",
            "__base__",
            "this is log",
            {"my_field": "my_value"},
            "2025-01-02 03:04:05,123 this is log {'my_field': 'my_value'}",
        ),
    ],
)
def test_soft_format_ok(
    formatter: SoftFormatter,
    record: Record,
    expected_str: str,
) -> None:
    assert formatter.format(record) == expected_str


@pytest.fixture
def record_timezone() -> t.Optional[str]:
    return None  # disable utc timezone


@pytest.fixture
def fmt() -> t.Optional[str]:
    raise NotImplementedError


@pytest.fixture
def exclude() -> t.Optional[str]:
    raise NotImplementedError


@pytest.fixture
def formatter(fmt: t.Optional[str], exclude: t.Optional[str]) -> SoftFormatter:
    return SoftFormatter(fmt=fmt, exclude=exclude)
