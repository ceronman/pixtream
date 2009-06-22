from twisted.web.resource import Resource
from twisted.internet.abstract import isIPAddress

from pixtream.tracker.peermanager import PeerManager
from pixtream.tracker.jsonencoder import PixtreamJSONEncoder

class TrackerResource(Resource):
    isLeaf = True

    def __init__(self, request_interval):
        Resource.__init__(self)

        self._peer_manager = PeerManager(peer_timeout = request_interval)
        self._encoder = PixtreamJSONEncoder()

    def _encode_peers(self):
        return self._encoder.encode(self._peer_manager)

    def _encode_failure(self, reason):
        answer = dict(failure_reason = reason)
        return self._encoder.encode(answer)

    def render_GET(self, request):
        args = request.args

        peer_id = args.get('peer_id', [None])[0]

        if peer_id is None:
            return self._encode_failure('Peer ID not given')

        if len(peer_id) != 20:
            return self._encode_failure('Invalid peer id')

        ip_address = args.get('ip', [request.getClientIP()])[0]

        if not isIPAddress(ip_address):
            return self._encode_failure('Invalid IP Address')

        port = args.get('port', [None])[0]

        if port is None:
            return self._encode_failure('Port number not given')

        try:
            port = int(port)
        except ValueError:
            return self._encode_failure('Invalid port number')

        self._peer_manager.update_peer(peer_id, ip_address, port)

        return self._encode_peers()

