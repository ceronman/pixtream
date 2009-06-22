from uuid import uuid4

from twisted.application.service import Service

class PeerService(Service):
    def __init__(self, tracker_url, port, ip):
        self.peers = []
        self.tracker_url = tracker_url
        self.port = port
        self.ip = ip
        self.peer_id = self.generate_peer_id()

        self.i = 0
        self.test_timer.start(self)

    def generate_peer_id(self):
        id = uuid4().hex
        id = id[:16]
        return 'PXTM' +  id


