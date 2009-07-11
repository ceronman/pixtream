"""
Script to launch a standalone program of a Pixtream Peer.

Use the run() method to launch the program.
"""

from optparse import OptionParser
import logging
import sys

from twisted.internet import reactor

from pixtream.peer.peerservice import PeerService

def _parse_options():
    parser = OptionParser()
    parser.usage = "usage: %prog [options] tracker_url"

    parser.add_option('-i', '--ip', dest='ip',
                      type='string',
                      help='IP Address to use', metavar='ADDRESS')

    parser.add_option('-p', '--port', dest='port',
                      type='int', default=60000,
                      help='Listening Port', metavar='PORT')

    parser.get_usage()

    options, args = parser.parse_args()

    if len(args) == 0:
        parser.error('Missing tracker argument')

    if len(args) > 1:
        parser.error('Too much arguments')

    return options.ip, options.port, args[0]

def _setup_logger():
    format = '%(asctime)s:%(levelname)s:%(module)s:%(lineno)d: %(message)s'
    logging.basicConfig(level = logging.DEBUG,
                        format = format,
                        stream = sys.stdout)

def run():
    """Runs a peer program."""
    _setup_logger()
    ip, port, tracker = _parse_options()
    service = PeerService(ip, port, tracker)
    service.listen()
    service.connect_to_tracker()

    print 'Running peer on port {0} with tracker: {1}'.format(port, tracker)
    print 'Press CTRL-C to quit'
    reactor.run()
