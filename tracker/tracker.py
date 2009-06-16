import time
import json
from threading import Timer
from twisted.web import server, resource
from twisted.internet import reactor

PEER_TIMEOUT = 30

class Peer(object):
    def __init__(self, peer_id, ip, port, last_update):
        self.id = peer_id
        self.ip = ip
        self.port = port
        self.last_update = last_update

class PeerManager(object):
    def __init__(self):
        self.peers = {}
        self.install_check_timer()

    def install_check_timer(self):
        timer = Timer(30, self.check_peers_timeout)
        timer.daemon = True
        timer.start()

    def check_peers_timeout(self):
        check_time = time.time()
        peer_to_delete = (peer_id for peer_id, peer in self.peers.items()
                          if check_time - peer.last_update > PEER_TIMEOUT)

        for peer_id in peer_to_delete:
            del self.peers[peer_id]

        self.install_check_timer()

    def update_peer(self, peer_id, ip, port):
        peer = Peer(peer_id, ip, port, time.time())
        self.peers[peer_id] = peer

class PeerManagerEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Peer):
            return dict(id = obj.id, ip = obj.ip, port = obj.port)
        if isinstance(obj, PeerManager):
            return obj.peers.values()
        return json.JSONEncoder.default(self, obj)

class TrackerResource(resource.Resource):
    isLeaf = True

    def __init__(self):
        self.peer_manager = PeerManager()

    def encode_peers(self):
        return json.dumps(self.peer_manager, cls=PeerManagerEncoder)

    def encode_failure(self, reason):
        answer = dict(failure_reason = reason)
        return json.dump(answer)

    def render_GET(self, request):
        args = request.args
        peer_id = args.get('peer_id', [None])
        ip = args.get('ip', [None])
        port = args.get('port', [None])
        peer_id, ip, port = peer_id[0], ip[0], port[0]
        ip = ip if ip is not None else request.getClientIP()

        if peer_id is None:
            return self.encode_failure('Peer ID not found')
        if port is None:
            return self.encode_failure('Port Number not found')

        self.peer_manager.update_peer(peer_id, ip, port)

        return self.encode_peers()

site = server.Site(TrackerResource())
reactor.listenTCP(8080, site)
reactor.run()

