"""
Script to launch a standalone program of a Pixtream Peer.

Use the run() method to launch the program.
"""

from twisted.internet import reactor

from pixtream.peer.peerservice import PeerService, SourcePeerService
from pixtream.peer.peerapplication import PeerApplication
from pixtream.peer import scriptutils

__all__ = ['run', 'run_source']

def run():
    """Runs a peer program."""
    scriptutils.setup_logger()
    ip, port, streaming_port, tracker = scriptutils.parse_options()
    service = PeerService(ip, port, tracker)
    app = PeerApplication()
    app.set_service(service)
    app.start_file_server('outtest')
    app.listen()
    app.connect_to_tracker()

    print 'Running peer on port {0} with tracker: {1}'.format(port, tracker)
    print 'Streaming server listening on port: {0}'.format(streaming_port)
    print 'Press CTRL-C to quit'
    reactor.run()

def run_source():
    """Runs a peer program."""

    scriptutils.setup_logger()
    (ip, port, streaming_port,
     tracker,
     source_type, source) = scriptutils.parse_source_options()

    service = SourcePeerService(ip, port, tracker)
    app = PeerApplication()
    app.set_service(service)
    app.start_http_server(streaming_port)
    app.listen() # TODO: listen(port)
    app.connect_to_tracker() # TODO: connect_to_tracker(tracker)

    if source_type == 'http':
        app.connect_to_http_source(source)
    if source_type == 'tcp':
        host, port = source.split(':')
        app.connect_to_tcp_source(host, int(port))
    if source_type == 'file':
        app.connect_to_file_source(source)

    print 'Running peer on port {0} with tracker: {1}'.format(port, tracker)
    print 'Streaming server listening on port: {0}'.format(streaming_port)
    print 'Press CTRL-C to quit'
    reactor.run()
