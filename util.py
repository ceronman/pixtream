import functools
from twisted.internet import reactor

def handle_exception(exception_class, handler):
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

class TwistedTimerException(Exception):
    pass

class TwistedTimer(object):
    def __init__(self, function, lapse):
        self.function = function
        self.lapse = lapse
        self.calling = False

    def repeater(self, *args, **kwargs)
        self.function(*args, **kwargs)
        self.call = reactor.callLater(selflapse, repeater)

    def call(self, *args, **kwargs):
        if self.calling:
            raise TwistedTimerException('Timer already called')
        self.repeater(*args, **kwargs)
        self.calling = True


