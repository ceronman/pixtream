"""
HTTP Server Test
"""

from twisted.web2.resource import Resource
from twisted.web2.http import Response
from twisted.web2.stream import ProducerStream
from twisted.web2.channel import HTTPFactory
from twisted.web2.server import Site
from twisted.internet import reactor

BUFFER_SIZE = 1000

class StreamingResource(Resource):
    addSlash = True

    def __init__(self, filename):
        self._filename = filename

    def render(self, request):
        stream = ProducerStream()
        media_file = open(self._filename, 'rb')
        stream.write(media_file.read())
        media_file.close()
        stream.finish()

        return Response(stream=stream)


if __name__ == '__main__':
    import sys

    site = Site(StreamingResource(sys.argv[1]))
    reactor.listenTCP(8081, HTTPFactory(site))
    reactor.run()
