from twisted.internet import reactor

class TwistedTimerException(Exception):
    pass

class TwistedTimer(object):
    def __init__(self, function, seconds):
        self.function = function
        self.seconds = seconds
        self.call = None

    def repeater(self, *args, **kwargs):
        self.call = reactor.callLater(self.seconds, self.repeater,
                                      *args, **kwargs)
        self.function(*args, **kwargs)

    def start(self, *args, **kwargs):
        if self.call is not None:
            raise TwistedTimerException('Timer already started')
        self.repeater(*args, **kwargs)
        self.calling = True

    def stop(self):
        if self.call is None:
            raise TwistedTimerException('Timer not started')
        self.call.cancel()
        self.call = None

    def delay(self, seconds):
        if self.call is None:
            raise TwistedTimerException('Call has not started')
        self.call.delay(seconds)

def timer(seconds):
    return lambda function: TwistedTimer(function, seconds)

