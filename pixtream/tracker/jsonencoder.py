from json import JSONEncoder

from pixtream.tracker.peermanager import Peer, PeerManager

class PixtreamJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Peer):
            return dict(id = obj.id, ip = obj.ip, port = obj.port)

        if isinstance(obj, PeerManager):
            return dict(request_interval = obj.peer_timeout,
                        peers = obj.peers.values())

        return super(PixtreamJSONEncoder, self).default(obj)

