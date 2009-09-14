"""
Takes a joined streaming data and serves it in an outgoing port
"""

from twisted.internet.protocol import Protocol, ServerFactory
from twisted.internet import reactor

__all__ = ['TCPStreamServer']

class TCPStreamServerProtocol(Protocol):

    def connectionMade(self):
        self.factory.connection_made(self)

    def send_stream(self, stream):
        self.transport.write(stream)

class StreamServer(object):

    def __init__(self, port):
        self.port = port
        self._connections = []
        # TODO: use a spooled file instead!!
        self._current_stream = bytes()

    def send_stream(self, stream):
        for connection in self._connections:
            connection.send_stream(stream)
        self._current_stream += stream

    def create_factory(self):
        pass

    def listen(self):
        reactor.listenTCP(self.port, self.create_factory())

    def close(self):
        for connection in self._connections:
            connection.loseConnection()

    def _connection_made(self, connection):
        connection.send_stream(self._current_stream)
        self._connections.append(connection)

class TCPStreamServer(StreamServer):

    def create_factory(self):
        factory = ServerFactory()
        factory.protocol = TCPStreamServerProtocol
        factory.connection_made = self._connection_made
        return factory

