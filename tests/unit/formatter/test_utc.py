import logging
from datetime import datetime, timezone

import pytest

from no_log_tears.formatter.utc import UTCTimeFormatter
from no_log_tears.record import Record


@pytest.mark.parametrize(
    ("time", "expected"),
    [
        pytest.param(
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            "2025-01-01T00:00:00.000000Z",
        ),
        pytest.param(
            datetime.fromisoformat("2025-02-18T17:43:37-05:00"),
            "2025-02-18T22:43:37.000000Z",
        ),
        pytest.param(
            datetime(2025, 2, 18, 22, 43, 37, tzinfo=timezone.utc),
            "2025-02-18T22:43:37.000000Z",
        ),
        pytest.param(
            datetime.fromisoformat("2025-02-18T22:45:22.123456+00:00"),
            "2025-02-18T22:45:22.123456Z",
        ),
    ],
)
def test_utc_ok(formatter: UTCTimeFormatter, record: Record, expected: str) -> None:
    assert formatter.formatTime(record) == expected


@pytest.fixture
def formatter() -> UTCTimeFormatter:
    return UTCTimeFormatter()


@pytest.fixture
def record(time: datetime) -> Record:
    rec = Record("test", logging.INFO, "path", 1, "test time")

    rec.created = time.timestamp()
    rec.msecs = (rec.created - int(rec.created)) * 1000

    return rec
