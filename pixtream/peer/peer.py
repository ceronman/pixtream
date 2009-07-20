"""
Script to launch a standalone program of a Pixtream Peer.

Use the run() method to launch the program.
"""

from twisted.internet import reactor

from pixtream.peer.peerservice import PeerService
from pixtream.peer import scriptutils

def run():
    """Runs a peer program."""
    scriptutils.setup_logger()
    ip, port, tracker = scriptutils.parse_options()
    service = PeerService(ip, port, tracker)
    service.listen()
    service.connect_to_tracker()

    print 'Running peer on port {0} with tracker: {1}'.format(port, tracker)
    print 'Press CTRL-C to quit'
    reactor.run()
