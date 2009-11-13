"""
A peer application
"""

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

    def connect_to_source(self, host, port):
        self._peer.stream_client.connect(host, port)

    def connect_to_url(self, url):
        self._peer.stream_client.connect(url)

    def connect_to_file(self, filename):
        self._peer.stream_client.open_file(filename)
