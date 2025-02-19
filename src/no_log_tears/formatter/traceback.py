"""Provides traceback formatter."""

import abc
import logging
import traceback
import typing as t
from collections import deque
from itertools import islice
from types import TracebackType

from typing_extensions import override


class TracebackGenerator(t.Protocol):
    """Interface to generate traceback parts from exception info."""

    @abc.abstractmethod
    def __call__(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType,
    ) -> t.Iterable[str]:
        """Generate traceback parts from exception info."""
        raise NotImplementedError


class TracebackFormatter(logging.Formatter):
    """
    Formatter to format traceback exception info to human-readable traceback.

    Traceback lines are limited by `traceback_tail` parameter. If `traceback_tail` is `None` - no limit is applied.
    Header and tail lines are always included. If traceback is limited - `... (xN stack frames)` line is added.
    """

    # NOTE: ignore PLR0913, because formatter can be constructed via dict configurator.
    def __init__(  # noqa: PLR0913
        self,
        fmt: t.Optional[str] = None,
        datefmt: t.Optional[str] = None,
        style: t.Literal["%", "{", "$"] = "%",
        validate: bool = True,  # noqa: FBT001,FBT002
        traceback_tail: t.Optional[int] = None,
        traceback_generator: t.Optional[TracebackGenerator] = None,
    ) -> None:
        """TracebackFormatter constructor."""
        super().__init__(fmt, datefmt, style, validate)
        self.__tail = traceback_tail + 1 if traceback_tail is not None else None
        self.__generator = traceback_generator if traceback_generator is not None else self.__generate_traceback

    @override
    def formatException(
        self,
        exc_info: t.Union[
            tuple[type[BaseException], BaseException, t.Optional[TracebackType]],
            tuple[None, None, None],
            bool,
            None,
        ],
    ) -> str:
        """Format exception to human-readable traceback text."""
        if not isinstance(exc_info, tuple):
            return ""

        exc_type, exc_value, exc_traceback = exc_info
        if exc_type is None or exc_value is None or exc_traceback is None:
            return ""

        tb_parts = list(self.__generator(exc_type, exc_value, exc_traceback))

        return "".join(self.__keep_top_and_last(tb_parts, self.__tail) if self.__tail is not None else tb_parts)

    def __keep_top_and_last(self, tb_parts: t.Iterable[str], n: int) -> t.Iterable[str]:
        iterator = iter(tb_parts)

        yield from islice(iterator, self.__tail)

        tail = deque(islice(iterator, n), maxlen=n)

        if len(tail) >= n:
            skip_count = 0
            for part in iterator:
                tail.popleft()
                skip_count += 1
                tail.append(part)

            if skip_count > 0:
                yield f"  ... (x{skip_count} stack frames)\n"

        yield from tail

    def __generate_traceback(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType,
    ) -> t.Iterable[str]:
        return traceback.TracebackException(exc_type, exc_value, exc_traceback).format()
