"""
Takes a joined streaming data and serves it in an outgoing port
"""

from twisted.web2.resource import Resource
from twisted.web2.stream import ProducerStream
from twisted.web2.http import Response
from twisted.web2.channel import HTTPFactory
from twisted.web2.server import Site
from twisted.internet.protocol import Protocol, ServerFactory
from twisted.internet import reactor

__all__ = ['TCPStreamServer', 'HTTPStreamServer', 'FileStreamServer']

class StreamServer(object):
    def __init__(self):
        # TODO: use a spooled file instead!!
        self._current_stream = bytes()

    def send_stream(self, data):
        pass

    def start(self):
        pass

    def stop(self):
        pass

class TCPStreamServer(StreamServer):

    class TCPStreamServerProtocol(Protocol):

        def connectionMade(self):
            self.factory.connection_made(self)

        def send_stream(self, stream):
            self.transport.write(stream)

    def __init__(self, port):
        super(TCPStreamServer, self).__init__()
        self._port = port
        self._connections = []

    def send_stream(self, data):
        for connection in self._connections:
            connection.send_stream(data)
        self._current_stream += data

    def start(self):
        reactor.listenTCP(self._port, self._create_factory())

    def stop(self):
        for connection in self._connections:
            connection.loseConnection()

    def _connection_made(self, connection):
        connection.send_stream(self._current_stream)
        self._connections.append(connection)

    def _create_factory(self):
        factory = ServerFactory()
        factory.protocol = self.TCPStreamServerProtocol
        factory.connection_made = self._connection_made
        return factory

class HTTPStreamServer(StreamServer):

    class StreamingResource(Resource):
        addSlash = True

        def __init__(self, server):
            self.server = server

        def render(self, request):
            producer = ProducerStream()
            self.server._append_producer(producer)
            producer.write(self.server._current_stream)

            return Response(stream=producer)

    def __init__(self, port):
        super(HTTPStreamServer, self).__init__()
        self._port = port
        self._producers = []

    def send_stream(self, data):
        for producer in self._producers:
            producer.write(data)
        self._current_stream += data

    def start(self):
        site = Site(self.StreamingResource(self))
        reactor.listenTCP(self._port, HTTPFactory(site))

    def stop(self):
        for producer in self._producers:
            producer.finish()
        self._producers = []

    def _append_producer(self, producer):
        self._producers.append(producer)

class FileStreamServer(StreamServer):

    def __init__(self, filename):
        super(FileStreamServer, self).__init__()
        self._filename = filename
        self._file = None

    def send_stream(self, data):
        if self._file:
            self._file.write(data)

    def start(self):
        self._file = open(self._filename, 'wb')

    def stop(self):
        self._file.close()

