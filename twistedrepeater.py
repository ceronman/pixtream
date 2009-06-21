from twisted.internet import reactor

class TwistedRepeaterException(Exception):
    pass

class TwistedRepeater(object):
    def __init__(self, function, seconds=None):
        self.function = function
        self.seconds = seconds
        self.call = None

    def repeater(self, *args, **kwargs):
        if self.seconds is not None:
            self.call = reactor.callLater(self.seconds, self.repeater,
                                          *args, **kwargs)
        self.function(*args, **kwargs)

    def start(self, *args, **kwargs):
        if self.call is not None:
            raise TwistedRepeaterException('Timer already started')
        self.repeater(*args, **kwargs)
        self.calling = True

    def stop(self):
        if self.call is None:
            raise TwistedRepeaterException('Timer not started')
        self.call.cancel()
        self.call = None

    def delay(self, seconds):
        if self.call is None:
            raise TwistedRepeaterException('Call has not started')
        self.call.delay(seconds)

def repeater(seconds):
    return lambda function: TwistedRepeater(function, seconds)

