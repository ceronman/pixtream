import collections

class Peer(object):
    def __init__(self, id, ip, port):
        self.id = id
        self.ip = ip
        self.port = port

class PeerDatabase(object):
    def __init__(self):
        self.clear()

    def add_peer(self, peer):
        assert isinstance(peer, Peer)
        self._id_index[peer.id] = peer

    def add_peers(self, peers):
        assert isinstance(peers, collections.Iterable)

        for peer in peers:
            assert isinstance(peer, Peer)
            self.add_peer(peer)

    def remove_peer(self, id):
        assert isinstance(id, str)
        assert len(id) == 20

        if id in self:
            del self._id_index[id]

    def remove_peers(self, ids):
        assert isinstance(ids, collections.Iterable)

        for id in ids:
            self.remove_peer(id)

    def clear(self):
        self._id_index = {}

    def update_peers(self, peers):
        self.clear()
        self.add_peers(peers)

    def get_peer(self, id):
        return self._id_index.get(id, None)

    def __contains__(self, id):
        return id in self._id_index

    @property
    def peer_ids(self):
        return set(self._id_index.iterkeys())


