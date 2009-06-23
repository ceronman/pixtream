from uuid import uuid4

from twisted.application.service import Service

from pixtream.peer.trackermanager import TrackerManager

def generate_peer_id():
    id = uuid4().hex
    id = id[:16]
    return 'PXTM' +  id

class PeerService(Service):
    def __init__(self, ip, port, tracker_url):
        self.peers = []
        self.port = port
        self.ip = ip
        self.peer_id = generate_peer_id()

        self._tracker_manager = TrackerManager(self, tracker_url)

    def connect_to_tracker(self):
        self._tracker_manager.connect_to_tracker()




