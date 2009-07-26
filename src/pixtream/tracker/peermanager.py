"""Defines a Peer and PeerManager class to maintain a peer list"""

import time

from pixtream.util.twistedrepeater import repeater

class Peer(object):
    """
    A simple Peer class for the tracker
    """

    def __init__(self, peer_id, ip, port, last_update):
        """
        Creates the Peer

        :param peer_id: 20 bytes ID of the peer
        :param ip: The IP address of the peer
        :param port: The port where the peer is listening
        :param last_update: timestamp of the last update
        """

        self.id = peer_id
        self.ip = ip
        self.port = port
        self.last_update = last_update

class PeerManager(object):
    """
    Manages a list of peers
    """

    def __init__(self, peer_timeout=30):
        """Inits the peer list"""

        self.peers = {}
        self.peer_timeout = peer_timeout

        self._check_peers_timeout.start_now(self)

    @repeater(1)
    def _check_peers_timeout(self):
        check_time = time.time()
        for peer in self.peers.values():
            if check_time - peer.last_update > self.peer_timeout + 10:
                del self.peers[peer.id]

    def update_peer(self, peer_id, ip, port):
        """Receives an update of a Peer"""
        peer = Peer(peer_id, ip, port, time.time())
        self.peers[peer_id] = peer

