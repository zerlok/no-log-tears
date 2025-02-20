from datetime import datetime, timezone

import pytest

from no_log_tears.formatter.datetime import ISO8601DatetimeFormatter
from no_log_tears.record import Record


@pytest.mark.parametrize(
    ("record_time", "expected"),
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
def test_utc_ok(formatter: ISO8601DatetimeFormatter, record: Record, expected: str) -> None:
    assert formatter.formatTime(record) == expected


@pytest.fixture
def formatter() -> ISO8601DatetimeFormatter:
    return ISO8601DatetimeFormatter()
