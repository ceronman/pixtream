"""
Clients for ordinary streaming systems
"""

import urlparse

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor, defer
from twisted.web.client import HTTPPageDownloader, HTTPClientFactory

from pixtream.util.event import Event

__all__ = ['TCPStreamClient', 'HTTPStreamClient']

class StreamClient(object):

    def __init__(self):
        self.on_stream_received = Event()
        self.on_stream_end = Event()

    def _data_received(self, data):
        self.on_data_received.call(data)

    def _connection_lost(self):
        self.on_stream_end.call()

class TCPStreamClient(StreamClient):

    class TCPStreamClientProtocol(Protocol):

        def dataReceived(self, data):
            self.factory._data_received(data)

        def connectionLost(self, reason):
            self.factory._connection_lost()

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
