'''
Simple event class
'''

class Event(object):

    def __init__(self):
        self.handlers = []

    def add_handler(self, handler):
        self.handlers.append(handler)

    def remove_handler(self, handler):
        self.handlers.remove(handler)

    def call(self, *args, **kwargs):
        for handler in self.handlers:
            handler(*args, **kwargs)
