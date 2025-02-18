from __future__ import annotations

import logging
import typing as t
from types import TracebackType


class Record(logging.LogRecord):
    # noinspection PyMethodParameters
    def __init__(
        _self,
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
        super().__init__(_name, _level, _pathname, _lineno, _msg, _args, _exc_info, _func, _sinfo)

        if _extra:
            for key, value in _extra.items():
                setattr(_self, key, value)

        for key, value in kwargs.items():
            setattr(_self, key, value)
