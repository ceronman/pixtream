import logging

from twisted.internet.protocol import ServerFactory, ClientFactory
from twisted.internet import reactor

from pixtream.peer.protocol import PixtreamProtocol
from pixtream.util.twistedrepeater import TwistedRepeater

CHECK_INTERVAL = 5

class ConnectionManager(object):

    def __init__(self, peer_service):
        self._peer_service = peer_service
        self.active_connections = {}
        self._checker_repeater = TwistedRepeater(self.check_connections,
                                                 CHECK_INTERVAL)
        self._checker_repeater.start_later()

    def configure_factory(self, factory):
        factory.protocol = PixtreamProtocol
        factory.peer_id = self._peer_service.peer_id
        factory.add_connection = self.add_connection
        factory.remove_connection = self.remove_connection
        factory.allow_connection = self.allow_connection

    def create_server_factory(self):
        factory = ServerFactory()
        self.configure_factory(factory)
        factory.target_id = None

        return factory

    def create_client_factory(self, target_id):
        factory = ClientFactory()
        self.configure_factory(factory)
        factory.target_id = target_id

        return factory

    def add_connection(self, connection):
        assert isinstance(connection, PixtreamProtocol)
        assert hasattr(connection, 'other_id')
        assert isinstance(connection.other_id, str)

        if connection.other_id in self.active_connections:
            logging.error('Trying to add an existing connection')
            connection.drop()
            return

        self.active_connections[connection.other_id] = connection

    def remove_connection(self, connection):
        assert isinstance(connection, PixtreamProtocol)
        assert hasattr(connection, 'other_id')
        assert isinstance(connection.other_id, str)

        self.active_connections.pop(connection.other_id, None)

    def allow_connection(self, peer_id):
        return peer_id not in self.active_connections

    def check_connections(self):
        connections = self.active_connections.keys()
        logging.debug('Active connections ' + str(connections))
        self._contact_peers()

    def listen(self):
        factory = self.create_server_factory()
        reactor.listenTCP(self._peer_service.port, factory)

    def connect_to_peer(self, peer):
        factory = self.create_client_factory(peer.id)
        reactor.connectTCP(peer.ip, peer.port, factory)

    def _contact_peers(self):
        available_peers = self._peer_service.available_peers
        contacted_peers = set(self.active_connections.iterkeys())

        not_contacted_peers = [peer for peer in available_peers
                               if peer.id not in contacted_peers]

        for peer in not_contacted_peers:
            self.connect_to_peer(peer)
