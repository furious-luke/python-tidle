from functools import wraps

from .memory import MemoryMetrics


def memory_metrics(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tmpl = 'measure#memory-increase=%dkb func={}'.format(func.__name__)
        with MemoryMetrics(tmpl):
            return func(*args, **kwargs)
    return wrapper
