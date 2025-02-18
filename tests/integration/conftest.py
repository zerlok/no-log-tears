import logging
import typing as t

import pytest
from _pytest.logging import LogCaptureFixture

from tests.stub.users import UserRegistry


@pytest.fixture
def user_registry() -> UserRegistry:
    return UserRegistry()


@pytest.fixture
def capture_logs(caplog: LogCaptureFixture) -> t.Iterator[LogCaptureFixture]:
    with caplog.at_level(logging.NOTSET):
        yield caplog
