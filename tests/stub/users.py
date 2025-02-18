import typing as t

from no_log_tears.mixin import LogMixin


class UserRegistry(LogMixin):
    def __init__(self) -> None:
        self.__users = dict[str, int]()

    def add(self, name: str) -> int:
        user_id = self.__users[name] = len(self.__users)
        self._log.info("user added", user_id=user_id, username=name)
        return user_id

    def get(self, name: str) -> t.Optional[int]:
        log = self._log(username=name)

        user_id = self.__users.get(name)

        if user_id is None:
            log.warning("user id was not found")
        else:
            log.debug("user was found", user_id=user_id)

        return user_id

    def _log_extra(self) -> t.Mapping[str, object]:
        return {"users_len": len(self.__users)}
