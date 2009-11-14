"""
Clients for ordinary streaming systems
"""

import urlparse

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor, defer
from twisted.web.client import HTTPPageDownloader, HTTPClientFactory

from pixtream.util.event import Event
from pixtream.util.twistedrepeater import TwistedRepeater

__all__ = ['TCPStreamClient', 'HTTPStreamClient']

class StreamClient(object):

    def __init__(self):
        self.on_stream_received = Event()
        self.on_stream_end = Event()

    def _data_received(self, data):
        self.on_stream_received.call(data)

    def _connection_lost(self):
        self.on_stream_end.call()

class TCPStreamClient(StreamClient):

    class TCPStreamClientProtocol(Protocol):

        def dataReceived(self, data):
            self.factory.data_received(data)

        def connectionLost(self, reason):
            self.factory.connection_lost()

    def _create_factory(self):
        factory = ClientFactory()
        factory.protocol = self.TCPStreamClientProtocol
        factory.data_received = self._data_received
        factory.connection_lost = self._connection_lost
        return factory

    def connect(self, host, port):
        factory = self._create_factory()
        reactor.connectTCP(host, port, factory)

class _HTTPStreamDownloader(HTTPClientFactory):
    protocol = HTTPPageDownloader

    def __init__(self, url):
        HTTPClientFactory.__init__(self, url)
        self.deferred = defer.Deferred()
        self.waiting = 1

        self.on_page_part = Event()
        self.on_page_end = Event()

    def pageStart(self, partialContent):
        self.waiting = 0

    def pagePart(self, data):
        self.on_page_part.call(data)

    def pageEnd(self):
        self.on_page_end.call()
        self.deferred.callback(None)


class HTTPStreamClient(StreamClient):

    def connect(self, url):
        parts = urlparse.urlsplit(url)
        port = 80 if parts.port is None else parts.port
        host = parts.hostname
        factory = _HTTPStreamDownloader(url)
        factory.on_page_part = self.on_stream_received
        factory.on_page_end = self.on_stream_end
        reactor.connectTCP(host, port, factory)

class FileStreamClient(StreamClient):

    # TODO change this to a config file
    BUFFER = 1000000
    INTERVAL = 1

    def __init__(self):
        super(FileStreamClient, self).__init__()
        self.stream  = None
        self.reader = None

    def open_file(self, filename):
        self.stream = open(filename, 'rb')
        self.reader = TwistedRepeater(self._read_file, self.INTERVAL)
        self.reader.start_later()

    def _stop_reader(self):
        if self.reader is not None:
            self.reader.stop()

    def _read_file(self):
        if not self.stream:
            self._stop_reader()
            return

        data = self.stream.read(self.BUFFER)

        if len(data) > 0:
            self.on_stream_received.call(data)

        else:
            self.on_stream_end.call()
            self.stream.close()
            self._stop_reader()
