from optparse import OptionParser

from twisted.web import server
from twisted.internet import reactor

from pixtream.tracker.resource import TrackerResource

def _parse_options():
    parser = OptionParser()

    parser.add_option('-p', '--port', dest='port',
                      type='int', default=8080,
                      help='Listening Port', metavar='PORT')

    parser.add_option('-i', '--interval', dest='interval',
                      type='int', default=30,
                      help='Interval in seconds for peers to make requests',
                      metavar='INTERVAL')

    return parser.parse_args()

def run():
    options, args = _parse_options()

    site = server.Site(TrackerResource(options.interval))
    reactor.listenTCP(options.port, site)
    reactor.run()

