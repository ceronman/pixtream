from optparse import OptionParser
from peer import PeerService
from twisted.internet import reactor

def parse_options():
    parser = OptionParser()

    parser.add_option('-t', '--tracker', dest='tracker_url',
                      type='string', default='',
                      help='The tracker url', metavar='URL')

    parser.add_option('-i', '--ip', dest='ip',
                      type='string', default='',
                      help='IP Address to use', metavar='ADDRESS')

    parser.add_option('-p', '--port', dest='port',
                      type='int', default=6000,
                      help='Listening Port', metavar='PORT')

    return parser.parse_args()


if __name__ == '__main__':
    options, args = parse_options()

    service = PeerService(options.tracker_url, options.port, options.ip)
    service.contact_tracker()
    reactor.run()
