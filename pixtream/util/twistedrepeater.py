"""
twistedrepeater.py

Creates a method that is repeated every n seconds using Twisted
reactor.callLater().
"""

from twisted.internet import reactor

class TwistedRepeaterException(Exception):
    """
    Errors produced by TwistedRepeater
    """
    pass

class TwistedRepeater(object):
    """
    Repeats a functions every n seconds using Twisted reactor

    Properties:

     - seconds:  define the time interval between calls.
     - function: function supposed to be called during the intervals.
    """

    def __init__(self, function, seconds=None):
        """
        Initializes the repeater.
        @param function: The function to be called.
        @param seconds: Interval in seconds between calls.
        """

        self.function = function
        self.seconds = seconds
        self.call = None

    def _repeater(self, *args, **kwargs):
        if self.seconds is not None:
            self.call = reactor.callLater(self.seconds, self._repeater,
                                          *args, **kwargs)
        self.function(*args, **kwargs)

    def start(self, *args, **kwargs):
        """Starts the repeater with given arguments"""

        if self.call is not None:
            raise TwistedRepeaterException('Timer already started')
        self._repeater(*args, **kwargs)
        self.calling = True

    def stop(self):
        """Stops the repeater"""

        if self.call is None:
            raise TwistedRepeaterException('Timer not started')
        self.call.cancel()
        self.call = None

    def delay(self, seconds):
        """Delays the next call to the repeater n seconds"""

        if self.call is None:
            raise TwistedRepeaterException('Call has not started')
        self.call.delay(seconds)

def repeater(seconds):
    """Convenience decorator for creating repeaters""" 
    return lambda function: TwistedRepeater(function, seconds)

