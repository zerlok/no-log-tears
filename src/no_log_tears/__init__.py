__all__ = [
    "LogMixin",
    "LoggableMixin",
    "Logger",
    "LoggerMixin",
    "get_logger",
]

from no_log_tears.config import DictConfigurator, is_autoload_enabled
from no_log_tears.logger import Logger, get_logger, patch_logging
from no_log_tears.mixin import LoggableMixin, LoggerMixin, LogMixin

patch_logging()

try:
    from no_log_tears.settings import Config
except ImportError:
    if is_autoload_enabled():
        DictConfigurator().configure()
else:
    if is_autoload_enabled():
        Config().configure()
