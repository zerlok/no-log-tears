import json
import sys
from unittest.mock import ANY

import pytest

from no_log_tears.formatter.json import JSONFormatter
from no_log_tears.record import Record


@pytest.mark.parametrize(
    ("record_extra", "expected_json"),
    [
        pytest.param(
            {},
            {
                "args": [],
                "asctime": ANY,
                "created": ANY,
                "exc_info": None,
                "exc_text": None,
                "filename": "path.py",
                "funcName": None,
                "levelname": "INFO",
                "levelno": 20,
                "lineno": 42,
                "module": "path",
                "msecs": ANY,
                "msg": "test-msg",
                "name": "test-record-name",
                "pathname": "/test/record/path.py",
                "process": ANY,
                "processName": "MainProcess",
                "relativeCreated": ANY,
                "stack_info": None,
                "taskName": None,
                "thread": ANY,
                "threadName": "MainThread",
            },
        ),
        pytest.param(
            {"custom_key_1": "custom_val_1", "custom_key_2": {"spam": "eggs"}},
            {
                "args": [],
                "asctime": ANY,
                "created": ANY,
                "custom_key_1": "custom_val_1",
                "custom_key_2": {"spam": "eggs"},
                "exc_info": None,
                "exc_text": None,
                "filename": "path.py",
                "funcName": None,
                "levelname": "INFO",
                "levelno": 20,
                "lineno": 42,
                "module": "path",
                "msecs": ANY,
                "msg": "test-msg",
                "name": "test-record-name",
                "pathname": "/test/record/path.py",
                "process": ANY,
                "processName": "MainProcess",
                "relativeCreated": ANY,
                "stack_info": None,
                "taskName": None,
                "thread": ANY,
                "threadName": "MainThread",
            },
        ),
    ],
)
def test_json_format_ok(
    formatter: JSONFormatter,
    record: Record,
    expected_json: dict[str, object],
) -> None:
    if sys.version_info < (3, 12):
        expected_json.pop("taskName", None)

    assert json.loads(formatter.format(record)) == expected_json


@pytest.fixture
def formatter() -> JSONFormatter:
    return JSONFormatter()
