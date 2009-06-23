from optparse import OptionParser

from twisted.internet import reactor

from pixtream.peer.peerservice import PeerService

def parse_options():
    parser = OptionParser()
    parser.usage = "usage: %prog [options] tracker_url"

    parser.add_option('-i', '--ip', dest='ip',
                      type='string',
                      help='IP Address to use', metavar='ADDRESS')

    parser.add_option('-p', '--port', dest='port',
                      type='int', default=6000,
                      help='Listening Port', metavar='PORT')

    parser.get_usage()

    options, args = parser.parse_args()

    if len(args) == 0:
        parser.error('Missing tracker argument')

    if len(args) > 1:
        parser.error('Too much arguments')

    return options.ip, options.port, args[0]


def run():
    ip, port, tracker = parse_options()
    service = PeerService(ip, port, tracker)
    service.connect_to_tracker()
    reactor.run()
