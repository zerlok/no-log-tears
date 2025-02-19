"""Custom log record class."""

from __future__ import annotations

import logging
import typing as t

if t.TYPE_CHECKING:
    from types import TracebackType


class Record(logging.LogRecord):
    """
    Custom log record class with additional fields.

    Additional fields can be passed as keyword arguments. They will be set as attributes of the record.
    """

    # noinspection PyMethodParameters
    def __init__(
        # NOTE: prefix all args with `_` and ignore N805, because `self` and other keys can be provided in keyword
        # arguments.
        _self,  # noqa:N805
        _name: str,
        _level: int,
        _pathname: str,
        _lineno: int,
        _msg: object,
        _args: tuple[object, ...] = (),
        _exc_info: t.Union[
            tuple[type[BaseException], BaseException, TracebackType],
            tuple[None, None, None],
            None,
        ] = None,
        _func: t.Optional[str] = None,
        _sinfo: t.Optional[str] = None,
        _extra: t.Optional[t.Mapping[str, object]] = None,
        **kwargs: object,
    ) -> None:
        """Create custom log record."""
        super().__init__(_name, _level, _pathname, _lineno, _msg, _args, _exc_info, _func, _sinfo)

        if _extra:
            for key, value in _extra.items():
                setattr(_self, key, value)

        for key, value in kwargs.items():
            setattr(_self, key, value)
