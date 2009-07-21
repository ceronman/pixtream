"""
Controls the peer application

It manages the Tracker Manager and the Connection Manager
"""

import logging
from uuid import uuid4

from pixtream.peer.trackermanager import TrackerManager
from pixtream.peer.peerdatabase import PeerDatabase
from pixtream.peer.connectionmanager import ConnectionManager
from pixtream.util.event import Event

class PeerService(object):
    """
    Controls every aspect of the peer application.
    """

    def __init__(self, ip, port, tracker_url):
        """
        Inits the Peer application.

        :param ip: The IP address of the peer.
        :param port: The port to listen.
        :param tracker_url: The URL of the tracker.
        """

        self.port = port
        self.ip = ip
        self._generate_peer_id()
        self._create_connection_manager()
        self._create_tracker_manager(tracker_url)

        self.available_peers = PeerDatabase()
        self.on_tracker_update = Event()
        self.on_peers_update = Event()

    @property
    def incoming_peers(self):
        """Returns a list of the IDs of the incomming connected peers"""
        return self.connection_manager.incoming_connections.ids

    @property
    def outgoing_peers(self):
        """Returns a list of the IDs of the incomming connected peers"""
        return self.connection_manager.outgoing_connections.ids

    def listen(self):
        """Starts listening on the selected port"""
        self.connection_manager.listen()

    def connect_to_tracker(self):
        """Contact the tracker for first time"""
        self._tracker_manager.connect_to_tracker()

    def _update_peers(self, sender, peer_list):
        """Hander to be called when the tracker is updated"""
        self.available_peers.update_peers(peer_list)
        self.available_peers.remove_peer(self.peer_id)
        logging.debug('Tracker updated: ' + str(self.available_peers.peer_ids))
        self.on_tracker_update.call(self)

    def _update_connections(self, sender):
        self.on_peers_update.call(self)

    def _generate_peer_id(self):
        id = uuid4().hex
        id = id[:14]
        self.peer_id = 'PX0001' +  id

    def _create_connection_manager(self):
        self.connection_manager = ConnectionManager(self)
        self.connection_manager.on_update.add_handler(self._update_connections)

    def _create_tracker_manager(self, tracker_url):
        self._tracker_manager = TrackerManager(self, tracker_url)
        self._tracker_manager.on_updated.add_handler(self._update_peers)
