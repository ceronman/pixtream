"""
Clients for ordinary streaming systems
"""

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor

__all__ = ['TCPStreamClient']

class TCPStreamClientProtocol(Protocol):

    def dataReceived(self, data):
        self.factory.data_received(data)

    def connectionLost(self, reason):
        self.factory.connection_lost()

# TODO: remove splitter dependency
class StreamClient(object):

    def __init__(self, splitter):
        self.splitter = splitter

    def data_received(self, data):
        self.splitter.push_stream(data)

    def connection_lost(self):
        self.splitter.end_stream()

class TCPStreamClient(StreamClient):

    def create_factory(self):
        factory = ClientFactory()
        factory.protocol = TCPStreamClientProtocol
        factory.data_received = self.data_received
        factory.connection_lost = self.connection_lost
        return factory

    def connect(self, host, port):
        factory = self.create_factory()
        reactor.connectTCP(host, port, factory)

