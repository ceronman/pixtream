import time

from pixtream.util.twistedrepeater import repeater

class Peer(object):
    def __init__(self, peer_id, ip, port, last_update):
        self.id = peer_id
        self.ip = ip
        self.port = port
        self.last_update = last_update

class PeerManager(object):
    def __init__(self, peer_timeout=30):
        self.peers = {}
        self.peer_timeout = peer_timeout

        self._check_peers_timeout.start(self)

    @repeater(1)
    def _check_peers_timeout(self):
        check_time = time.time()
        for peer in self.peers.values():
            if check_time - peer.last_update > self.peer_timeout:
                del self.peers[peer.id]

    def update_peer(self, peer_id, ip, port):
        peer = Peer(peer_id, ip, port, time.time())
        self.peers[peer_id] = peer

