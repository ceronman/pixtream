"""
Utilities for exception handling
"""

import functools

def handle_exception(exception_class, handler):
    """Decorator to handle an exception with a function"""

    if not isinstance(exception_class, Exception):
        exception_class = Exception
    if not hasattr(handler, '__call__'):
        def new_handler(e):
            raise e

        handler = new_handler

    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except exception_class as e:
                handler(e)

        return wrapper

    return decorator

