import inspect
import logging
import sys
from typing import Callable

LOG = logging.getLogger("client") if sys.argv[0].find("client.py") != 1 else logging.getLogger("server")


def log(func: Callable):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        LOG.debug(
            f"Функция <{func.__name__}> с параметрами <{args, kwargs}> из модуля <{func.__module__}> "
            f"из функции <{inspect.stack()[1][3]}>"
        )
        return result

    return wrapper
