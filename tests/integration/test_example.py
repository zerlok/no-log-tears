import logging

import pytest
from _pytest.logging import LogCaptureFixture

from tests.stub.users import UserRegistry


@pytest.mark.parametrize("username", ["John", "Arthur"])
def test_logging_ok(
    capture_logs: LogCaptureFixture,
    user_registry: UserRegistry,
    username: str,
) -> None:
    user_id = user_registry.add(username)

    assert [
        {
            "name": r.name,
            "level": r.levelno,
            "message": r.message,
            "funcName": r.funcName,
            "self": r.self,  # type: ignore[attr-defined]
            "user_id": r.user_id,  # type: ignore[attr-defined]
            "username": r.username,  # type: ignore[attr-defined]
            "users_len": r.users_len,  # type: ignore[attr-defined]
        }
        for r in capture_logs.records
    ] == [
        {
            "name": f"{UserRegistry.__module__}.{UserRegistry.__name__}",
            "level": logging.INFO,
            "message": "user added",
            "funcName": "add",
            "self": hex(id(user_registry)),
            "user_id": user_id,
            "username": username,
            "users_len": user_id + 1,
        }
    ]
