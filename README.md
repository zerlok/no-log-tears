# no log tears

[![Latest Version](https://img.shields.io/pypi/v/no-log-tears.svg)](https://pypi.python.org/pypi/no-log-tears)
[![Python Supported Versions](https://img.shields.io/pypi/pyversions/no-log-tears.svg)](https://pypi.python.org/pypi/no-log-tears)
[![MyPy Strict](https://img.shields.io/badge/mypy-strict-blue)](https://mypy.readthedocs.io/en/stable/getting_started.html#strict-mode-and-configuration)
[![Test Coverage](https://codecov.io/gh/zerlok/no-log-tears/branch/main/graph/badge.svg)](https://codecov.io/gh/zerlok/no-log-tears)
[![Downloads](https://img.shields.io/pypi/dm/no-log-tears.svg)](https://pypistats.org/packages/no-log-tears)
[![GitHub stars](https://img.shields.io/github/stars/zerlok/no-log-tears)](https://github.com/zerlok/no-log-tears/stargazers)

I personally found the built-in logging library to be a bit messy to use, so I created this library.
Now, logging is easy, and there are no more tears!

## Features

- **easy to configure**: set up logging via environment variables or a configuration file (thanks to pydantic-settings).
- **extended base configuration**:
    - **predefined configuration**: use built-in formatters and handlers or create your own.
    - **customizable default configuration with environment variables**: e.g. `LOGGING__LEVEL=INFO` and your process
      will log at the `INFO` level. Or `LOGGING__FORMATTER=verbose` to use the predefined `verbose` formatter.
    - **capture python warnings**: log `warnings.warn` messages to the logger.
- **mixins**: easily add logging to your classes.
    - **LoggerMixin**: adds `_logger` property to your instance and adds `self` to log records (instance hex id).
    - **LoggableMixin**: converts instance to string based on logging level of the class.
    - **LogMixin**: adds a `_log` to your class and allows you to bind additional context to loggers with `_log_extra`
      method.
- **log context**: easily bind additional context to loggers.
- **traceback limit**: Set the number of stack frames to display in log messages.

## Dependencies

- python 3.9+

Optional:

- pydantic
- pydantic-settings

## Installation

```bash
pip install no-log-tears
```

## Usage

Simple logging (execute python script with `LOGGING__LEVEL=INFO` environment variable):

```python
from no_log_tears import get_logger

log = get_logger(__name__)
log.info("Hello, world!")
# Output: `2025-02-19 20:42:28,928 INFO    __main__                                           Hello, world!`
```

Set up logging with a configuration file:

```yaml
# logging.yaml
root:
  level: INFO
  handlers: [ console ]
handlers:
  console:
    formatter: custom
    stream: ext://sys.stdout
formatters:
  custom:
    (): no_log_tears.formatters.SoftFormatter
    fmt: '%(asctime)s %(levelname)s %(message)s %(my_field)s %(__other__)s'
```

```python
# automatically loads logging configuration from `logging.yaml` on import
from no_log_tears import get_logger

log = get_logger(__name__)
log.info("Hello, world!", my_field="my_value", my_other_field="my_other_value")
# Output: `2025-02-19 20:42:28,928 INFO Hello, world! my_value {'my_other_field': 'my_other_value'}`
```

Use the `LogMixin` class to easily log messages with additional context:

```python
from no_log_tears import LogMixin


class MyClass(LogMixin):
    def __init__(self, my_field: str) -> None:
        self.__my_field = my_field

    def do_stuff(self, foo: str) -> str:
        # bind `foo` value to the logger
        log = self._log(foo=foo)

        # log a message with `foo` value
        log.debug("Doing stuff ...")

        spam = foo + ":eggs"
        log = log(spam=spam)

        # log a message with `foo`, `spam` and `magic` values
        log.info("Stuff done!", magic="Yes!")

        return spam
```
