"""
Script to launch a standalone program of a Pixtream Peer.

Use the run() method to launch the program.
"""

from twisted.internet import reactor

from pixtream.peer.peerservice import PeerService, SourcePeerService
from pixtream.peer import scriptutils

def run():
    """Runs a peer program."""
    scriptutils.setup_logger()
    ip, port, streaming_port, tracker = scriptutils.parse_options()
    service = PeerService(ip, port, tracker, int(streaming_port))
    service.listen()
    service.connect_to_tracker()

    print 'Running peer on port {0} with tracker: {1}'.format(port, tracker)
    print 'Press CTRL-C to quit'
    reactor.run()

def run_source():
    """Runs a peer program."""

    scriptutils.setup_logger()
    (ip, port, streaming_port,
     tracker,
     s_host, s_port) = scriptutils.parse_source_options()

    service = SourcePeerService(ip, port, tracker, int(streaming_port))
    service.listen()
    service.connect_to_tracker()
    service.connect_to_source(s_host, int(s_port))

    print 'Running peer on port {0} with tracker: {1}'.format(port, tracker)
    print 'Streaming server listening on port: {0}'.format(streaming_port)
    print 'Press CTRL-C to quit'
    reactor.run()
