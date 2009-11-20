"""
A peer application
"""

from pixtream.peer.streamclient import TCPStreamClient, HTTPStreamClient
from pixtream.peer.streamclient import FileStreamClient
from pixtream.peer.streamserver import TCPStreamServer, HTTPStreamServer
from pixtream.peer.streamserver import FileStreamServer
from pixtream.util.event import Event


__all__ = ['PeerApplication']

class PeerApplication(object):
    def __init__(self):
        self._peer = None

        self.on_tracker_update = Event()
        self.on_peers_update = Event()

    @property
    def incoming_peers(self):
        """Returns a list of the IDs of the incomming connected peers"""
        return self._peer.connection_manager.incoming_connections.ids

    @property
    def outgoing_peers(self):
        """Returns a list of the IDs of the incomming connected peers"""
        return self._peer.connection_manager.outgoing_connections.ids

    def set_service(self, peer_service):
        self._peer = peer_service

    def listen(self):
        """Starts listening on the selected port"""
        self._peer.connection_manager.listen(self._peer.port)

    def connect_to_tracker(self):
        """Contact the tracker for first time"""
        self._peer.tracker_manager.connect_to_tracker()

    def connect_to_tcp_source(self, host, port):
        client = TCPStreamClient()
        self._peer.attach_stream_client(client)
        self._peer.stream_client.connect(host, port)

    def connect_to_http_source(self, url):
        client = HTTPStreamClient()
        self._peer.attach_stream_client(client)
        self._peer.stream_client.connect(url)

    def connect_to_file_source(self, filename):
        client = FileStreamClient()
        self._peer.attach_stream_client(client)
        self._peer.stream_client.open_file(filename)

    def start_tcp_server(self, port):
        server = TCPStreamServer(port)
        self._peer.stream_server = server
        server.start()

    def start_http_server(self, port):
        server = HTTPStreamServer(port)
        self._peer.stream_server = server
        server.start()

    def start_file_server(self, filename):
        server = FileStreamServer(filename)
        self._peer.stream_server = server
        server.start()
