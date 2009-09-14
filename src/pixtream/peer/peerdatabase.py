"""
Defines a Peer Class and a collections of peers indexed by ID.
"""

import collections

__all__ = ['Peer', 'PeerDatabase']

class Peer(object):
    """
    Defines a peer as returned from the tracker.
    """

    def __init__(self, id, ip, port):
        """Creates a peer from an id, port and IP address."""

        self.id = id
        self.ip = ip
        self.port = port

class PeerDatabase(object):
    """
    Collections of peers indexed by ID.
    """

    def __init__(self):
        self._id_index = {}

        self.clear()

    def add_peer(self, peer):
        """Adds a peer object."""

        assert isinstance(peer, Peer)
        self._id_index[peer.id] = peer

    def add_peers(self, peers):
        """Adds a collections of peer objects."""

        assert isinstance(peers, collections.Iterable)

        for peer in peers:
            assert isinstance(peer, Peer)
            self.add_peer(peer)

    def remove_peer(self, id):
        """Removes a peer from its ID."""

        assert isinstance(id, str)
        assert len(id) == 20

        self._id_index.pop(id, None)

    def remove_peers(self, ids):
        """Given a collection of IDs, removes the peers."""
        assert isinstance(ids, collections.Iterable)

        for id in ids:
            self.remove_peer(id)

    def clear(self):
        """Removes all peers."""
        self._id_index.clear()

    def update_peers(self, peers):
        """Removes all peers and adds a new collections"""
        self.clear()
        self.add_peers(peers)

    def get_peer(self, id):
        """Returns a peer from its ID"""
        return self._id_index.get(id, None)

    def __contains__(self, id):
        return id in self._id_index

    def __iter__(self):
        return self._id_index.itervalues()

    @property
    def peer_ids(self):
        """Returns a set of all IDs of the peers"""
        return set(self._id_index.iterkeys())


