import logging
import typing as t
from datetime import datetime, timezone
from types import TracebackType

import pytest

from no_log_tears.record import Record


@pytest.fixture
def record_timezone() -> t.Optional[timezone]:
    return timezone.utc


@pytest.fixture
def record_time(record_timezone: t.Optional[timezone]) -> datetime:
    return datetime(2025, 1, 2, 3, 4, 5, 123456, tzinfo=record_timezone)


@pytest.fixture
def record_name() -> str:
    return "test-record-name"


@pytest.fixture
def record_level() -> int:
    return logging.INFO


@pytest.fixture
def record_path() -> str:
    return "/test/record/path.py"


@pytest.fixture
def record_line() -> int:
    return 42


@pytest.fixture
def record_msg() -> str:
    return "test-msg"


@pytest.fixture
def record_args() -> tuple[object, ...]:
    return ()


@pytest.fixture
def record_exc_info() -> tuple[type[BaseException], BaseException, TracebackType] | tuple[None, None, None] | None:
    return None


@pytest.fixture
def record_func() -> t.Optional[str]:
    return None


@pytest.fixture
def record_sinfo() -> t.Optional[str]:
    return None


@pytest.fixture
def record_extra() -> t.Mapping[str, object]:
    return {}


@pytest.fixture
def record_kwargs() -> t.Mapping[str, object]:
    return {}


@pytest.fixture
def record(
    record_time: datetime,
    record_name: str,
    record_level: int,
    record_path: str,
    record_line: int,
    record_msg: str,
    record_args: tuple[object, ...],
    record_exc_info: tuple[type[BaseException], BaseException, TracebackType] | tuple[None, None, None] | None,
    record_func: t.Optional[str],
    record_sinfo: t.Optional[str],
    record_extra: t.Mapping[str, object],
    record_kwargs: t.Mapping[str, object],
) -> Record:
    rec = Record(
        record_name,
        record_level,
        record_path,
        record_line,
        record_msg,
        record_args,
        record_exc_info,
        record_func,
        record_sinfo,
        record_extra,
        **record_kwargs,
    )

    rec.created = record_time.timestamp()
    rec.msecs = (rec.created - int(rec.created)) * 1000

    return rec
