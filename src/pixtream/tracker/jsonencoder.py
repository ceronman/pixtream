"""Defines JSON encoders for peer list data."""

from json import JSONEncoder

from pixtream.tracker.peermanager import Peer, PeerManager

class PixtreamJSONEncoder(JSONEncoder):
    """
    JSON Encoder for Peer and PeerManager
    """

    def default(self, obj):
        """Default handler for the encoder."""
        if isinstance(obj, Peer):
            return dict(id = obj.id,
                        ip = obj.ip,
                        port = obj.port,
                        utility_factor = obj.utility_factor)

        if isinstance(obj, PeerManager):
            return dict(request_interval = obj.peer_timeout,
                        peers = obj.peers.values())

        return super(PixtreamJSONEncoder, self).default(obj)

