import logging
from uuid import uuid4

from twisted.internet import reactor

from pixtream.peer.trackermanager import TrackerManager
from pixtream.peer.peerdatabase import PeerDatabase
from pixtream.peer.serverfactory import ServerFactory
from pixtream.peer.connectionmanager import ConnectionManager

class PeerService(object):
    def __init__(self, ip, port, tracker_url):
        self.port = port
        self.ip = ip
        self._generate_peer_id()
        self._create_connection_manager()
        self._create_server_factory()

        self._tracker_manager = TrackerManager(self, tracker_url)

        self._available_peers = PeerDatabase()

    def listen(self):
        reactor.listenTCP(self.port, self.server_factory)

    def connect_to_tracker(self):
        self._tracker_manager.connect_to_tracker()

    def tracker_updated(self):
        logging.debug('Peers updated')

        self._update_peers()

    def _update_peers(self):
        peer_list = self._tracker_manager.peer_list
        self._available_peers.update_peers(peer_list)
        self._available_peers.remove_peer(self.peer_id)
        logging.debug(str(self._available_peers.peer_ids))

    def _generate_peer_id(self):
        id = uuid4().hex
        id = id[:14]
        self.peer_id = 'PX0001' +  id

    def _create_server_factory(self):
        self.server_factory = ServerFactory(self)

    def _create_connection_manager(self):
        self.connection_manager = ConnectionManager(self)
