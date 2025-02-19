import sys
import traceback
import typing as t
from itertools import chain
from types import TracebackType

import pytest

from no_log_tears.formatter.traceback import TracebackFormatter


class CustomError(Exception):
    pass


ExceptionInfo = t.Union[tuple[type[CustomError], CustomError, t.Optional[TracebackType]], None]


@pytest.mark.parametrize(
    "stack",
    [
        pytest.param(1),
        pytest.param(2),
        pytest.param(5),
        pytest.param(6),
        pytest.param(10),
        pytest.param(100),
    ],
)
def test_full_traceback(
    formatter: TracebackFormatter,
    stack: int,
    exc_info: ExceptionInfo,
    exc_info_lines: t.Sequence[str],
) -> None:
    # skip `Traceback (most recent call last):` and last empty line.
    _, *lines, _ = formatter.formatException(exc_info).split("\n")

    assert lines == exc_info_lines


@pytest.mark.parametrize(
    ("stack", "traceback_tail"),
    [
        pytest.param(5, 1),
        pytest.param(10, 4),
        pytest.param(20, 5),
        pytest.param(100, 5),
        pytest.param(100, 10),
    ],
)
def test_traceback_is_limited(
    formatter: TracebackFormatter,
    stack: int,
    traceback_tail: int,
    exc_info: ExceptionInfo,
    exc_info_lines: t.Sequence[str],
) -> None:
    assert stack > traceback_tail

    # skip `Traceback (most recent call last):`
    _, *lines = formatter.formatException(exc_info).split("\n")

    # 1) each call stack is printed in 2 lines (File + code preview), thus divide lines by 2.
    # 2) `traceback_tail` applies for top and lower part of traceback, thus multiply it by 2.
    # *) +1 for extra line `~~~~^^^` in python 3.13 and higher.
    ratio = 2 + (sys.version_info >= (3, 13))

    # 3) extra middle `x{N} items`, thus +1.
    assert len(lines) // 2 == traceback_tail * ratio + 1

    # each stack frame has 2 lines in traceback.
    assert lines[len(lines) // 2 - 1] == f"  ... (x{(len(exc_info_lines) - len(lines)) // ratio + 1} stack frames)"


@pytest.fixture
def stack() -> t.Optional[int]:
    return None


@pytest.fixture
def traceback_tail() -> t.Optional[int]:
    return None


@pytest.fixture
def formatter(traceback_tail: t.Optional[int]) -> TracebackFormatter:
    return TracebackFormatter(traceback_tail=traceback_tail)


@pytest.fixture
def exc_info(stack: t.Optional[int]) -> ExceptionInfo:
    if stack is None:
        return None

    def build(n: int) -> None:
        if n >= 2:  # noqa: PLR2004
            # Declare anonymous function and invoke it, so traceback package won't deduplicate lines.
            # This call doubles stack trace.
            def inner() -> None:
                build(n - 2)

            inner()
        raise CustomError

    with pytest.raises(CustomError) as exc_info:  # noqa: PT012
        if stack < 2:  # noqa: PLR2004
            raise CustomError

        build(stack - 2)

    return exc_info.type, exc_info.value, exc_info.value.__traceback__


@pytest.fixture
def exc_info_lines(exc_info: ExceptionInfo) -> t.Sequence[str]:
    if exc_info is None:
        return []

    # skip `Traceback (most recent call last):`
    _, *lines = traceback.format_exception(*exc_info)

    # skip empty lines
    return [line for line in chain.from_iterable(line.split("\n") for line in lines) if line]
