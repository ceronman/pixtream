import logging
from uuid import uuid4

from twisted.application.service import Service

from pixtream.peer.trackermanager import TrackerManager
from pixtream.peer.peerdatabase import PeerDatabase

def generate_peer_id():
    id = uuid4().hex
    id = id[:16]
    return 'PXTM' +  id

class PeerService(Service):
    def __init__(self, ip, port, tracker_url):
        self.port = port
        self.ip = ip
        self.peer_id = generate_peer_id()

        self._tracker_manager = TrackerManager(self, tracker_url)

        self._available_peers = PeerDatabase()

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
