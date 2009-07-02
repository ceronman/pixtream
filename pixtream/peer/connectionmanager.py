import logging

from twisted.internet.protocol import ServerFactory, ClientFactory
from twisted.internet import reactor

from pixtream.peer.protocol import IncomingProtocol, OutgoingProtocol
from pixtream.util.twistedrepeater import TwistedRepeater
from pixtream.peer.peerdatabase import Peer

CHECK_INTERVAL = 5

class ConnectionManager(object):

    def __init__(self, peer_service):
        self.incoming_connections = {}
        self.outgoing_connections = {}

        self._peer_service = peer_service

        self._checker_repeater = TwistedRepeater(self.check_connections,
                                                 CHECK_INTERVAL)
        self._checker_repeater.start_later()

    @property
    def contacted_peers(self):
        return set(self.incoming_connections.keys() +
                   self.outgoing_connections.keys())

    def create_server_factory(self):
        factory = ServerFactory()
        factory.protocol = IncomingProtocol
        factory.peer_id = self._peer_service.peer_id
        factory.add_incoming_connection = self.add_incoming_connection
        factory.remove_incoming_connection = self.remove_incoming_connection
        factory.allow_connection = self.allow_connection

        return factory

    def create_client_factory(self, target_id):
        factory = ClientFactory()
        factory.protocol = OutgoingProtocol
        factory.peer_id = self._peer_service.peer_id
        factory.target_id = target_id
        factory.add_outgoing_connection = self.add_outgoing_connection
        factory.remove_outgoing_connection = self.remove_outgoing_connection
        factory.allow_connection = self.allow_connection

        return factory

    def add_incoming_connection(self, connection):
        assert isinstance(connection, IncomingProtocol)
        assert isinstance(connection.partner_id, str)

        if connection.partner_id in self.incoming_connections:
            logging.error('Adding nonexistent connection')
            connection.drop()
            return

        self.incoming_connections[connection.partner_id] = connection

    def remove_incoming_connection(self, connection):
        assert isinstance(connection, IncomingProtocol)
        assert isinstance(connection.partner_id, str)

        if connection.partner_id not in self.incoming_connections:
            logging.error('Removing nonexistent connection')
            return

        del self.incoming_connections[connection.partner_id]

    def add_outgoing_connection(self, connection):
        assert isinstance(connection, OutgoingProtocol)
        assert isinstance(connection.partner_id, str)

        if connection.partner_id in self.outgoing_connections:
            logging.error('Adding nonexistent connection')
            connection.drop()
            return

        self.outgoing_connections[connection.partner_id] = connection

    def remove_outgoing_connection(self, connection):
        assert isinstance(connection, OutgoingProtocol)
        assert isinstance(connection.partner_id, str)

        if connection.partner_id not in self.outgoing_connections:
            logging.error('Removing nonexistent connection')
            return

        del self.outgoing_connections[connection.partner_id]

    def allow_connection(self, peer_id):
        return peer_id not in self.contacted_peers

    def check_connections(self):
        incoming_connections = self.incoming_connections.keys()
        outgoing_connections = self.outgoing_connections.keys()
        logging.debug('Incoming connections ' + str(incoming_connections))
        logging.debug('Outgoing connections ' + str(outgoing_connections))
        self._contact_peers()

    def listen(self):
        factory = self.create_server_factory()
        reactor.listenTCP(self._peer_service.port, factory)

    def connect_to_peer(self, peer):
        assert isinstance(peer, Peer)

        logging.debug('Connecting to peer:' + peer.id)
        factory = self.create_client_factory(peer.id)
        reactor.connectTCP(peer.ip, peer.port, factory)

    def _contact_peers(self):
        available_peers = self._peer_service.available_peers

        not_contacted_peers = [peer for peer in available_peers
                               if peer.id not in self.contacted_peers]

        for peer in not_contacted_peers:
            self.connect_to_peer(peer)
