"""Twisted tracker resource. It handles HTTP request to the tracker"""

from twisted.web.resource import Resource
from twisted.internet.abstract import isIPAddress

from pixtream.tracker.peermanager import PeerManager
from pixtream.tracker.jsonencoder import PixtreamJSONEncoder

class TrackerResource(Resource):

    def __init__(self, peer_manager):
        Resource.__init__(self)
        self._peer_manager = peer_manager
        self._encoder = PixtreamJSONEncoder()

    def _encode_peers(self):
        return self._encoder.encode(self._peer_manager)

    def _encode_failure(self, reason):
        answer = dict(failure_reason = reason)
        return self._encoder.encode(answer)

    def _encode_success(self):
        return self._encoder.encode('success')

class UtilityFactorResource(TrackerResource):

    isLeaf = True

    def render_GET(self, request):
        utility_factors = {}

        for peer_id in request.args.keys():
            if not self._peer_manager.peer_exists(peer_id):
                return self._encode_failure('Peer in utility factors does not '
                                            'exist in the tracker')

            utility_factors[peer_id] = request.args[peer_id][0]

        if len(utility_factors) == 0:
            return self._encode_failure('No data provided')

        ip = request.getClientIP()

        self._peer_manager.report_utility_factors(ip, utility_factors)

        return self._encode_success()

class AnnounceResource(TrackerResource):

    isLeaf = True

    def render_GET(self, request):
        """Renders the response to peers"""
        args = request.args

        peer_id = args.get('peer_id', [None])[0]

        if peer_id is None:
            return self._encode_failure('Peer ID not given')

        if len(peer_id) != 20:
            return self._encode_failure('Invalid peer id')

        # TODO: eliminate ip option
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

class RootResource(Resource):

    def __init__(self, peer_timeout):
        Resource.__init__(self)
        self._peer_manager = PeerManager(peer_timeout)
#        self.putChild('announce', AnnounceResource(self._peer_manager))

    def getChild(self, name, request):
        if name == '':
            return self

        if name == 'announce':
            return AnnounceResource(self._peer_manager)

        if name == 'utility':
            return UtilityFactorResource(self._peer_manager)

        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        return 'Pixtream Tracker'
