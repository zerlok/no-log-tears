import json
import logging
import typing as t
from unittest.mock import ANY

import pytest

from no_log_tears.formatter.json import JSONFormatter
from no_log_tears.record import Record


@pytest.mark.parametrize(
    ("record", "expected_json"),
    [
        pytest.param(
            Record(
                "foo",
                logging.INFO,
                "/path/to/file.py",
                42,
                "log message",
            ),
            {
                "args": [],
                "asctime": ANY,
                "created": ANY,
                "exc_info": None,
                "exc_text": None,
                "filename": "file.py",
                "funcName": None,
                "levelname": "INFO",
                "levelno": 20,
                "lineno": 42,
                "module": "file",
                "msecs": ANY,
                "msg": "log message",
                "name": "foo",
                "pathname": "/path/to/file.py",
                "process": ANY,
                "processName": "MainProcess",
                "relativeCreated": ANY,
                "stack_info": None,
                "thread": ANY,
                "threadName": "MainThread",
            },
        ),
        pytest.param(
            Record(
                "foo",
                logging.INFO,
                "/path/to/file.py",
                42,
                "log message",
                custom_key_1="custom_val_1",
                custom_key_2={"spam": "eggs"},
            ),
            {
                "args": [],
                "asctime": ANY,
                "created": ANY,
                "custom_key_1": "custom_val_1",
                "custom_key_2": {"spam": "eggs"},
                "exc_info": None,
                "exc_text": None,
                "filename": "file.py",
                "funcName": None,
                "levelname": "INFO",
                "levelno": 20,
                "lineno": 42,
                "module": "file",
                "msecs": ANY,
                "msg": "log message",
                "name": "foo",
                "pathname": "/path/to/file.py",
                "process": ANY,
                "processName": "MainProcess",
                "relativeCreated": ANY,
                "stack_info": None,
                "thread": ANY,
                "threadName": "MainThread",
            },
        ),
    ],
)
def test_json_format_ok(
    formatter: JSONFormatter,
    record: Record,
    expected_json: t.Mapping[str, object],
) -> None:
    assert json.loads(formatter.format(record)) == expected_json


@pytest.fixture
def formatter() -> JSONFormatter:
    return JSONFormatter()
