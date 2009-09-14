"""
Manages incoming and outgoing connections to other peers.
"""

import logging
import itertools

from twisted.internet.protocol import ServerFactory, ClientFactory
from twisted.internet import reactor

from pixtream.util.event import Event
from pixtream.peer.protocol import IncomingProtocol, OutgoingProtocol

__all__ = ['ConnectionManager']

class ConnectionList(object):

    def __init__(self, protocol_class):
        self.on_changed = Event()
        self._connections = {}
        self._protocol_class = protocol_class

    def add(self, connection):
        """Adds a new item to the list of connections."""

        assert isinstance(connection, self._protocol_class)
        assert isinstance(connection.partner_id, str)

        if connection.partner_id in self._connections:
            logging.error('Adding existent connection')
            connection.drop()
            return

        self._connections[connection.partner_id] = connection
        self.on_changed.call(self)

    def remove(self, connection):
        """Removes an item from the list of connections."""

        assert isinstance(connection, self._protocol_class)
        assert isinstance(connection.partner_id, str)

        if connection.partner_id not in self._connections:
            logging.error('Removing nonexistent connection')
            return

        del self._connections[connection.partner_id]
        self.on_changed.call(self)

    def __iter__(self):
        return self._connections.itervalues()

    def __contains__(self, partner_id):
        return partner_id in self._connections

    def __getitem__(self, partner_id):
        return self._connections[partner_id]

    @property
    def ids(self):
        return self._connections.keys()

# TODO: Remove PeerService dependency
class ConnectionManager(object):
    """
    Maintains a collection of incoming and outgoing connections to a peer.
    """

    def __init__(self, peer_service):
        """
        Creates a new ConnectionManager object.
        """
        self.on_update = Event()

        self._peer_service = peer_service

        self._connection_attempts = set()

        self.incoming_connections = ConnectionList(IncomingProtocol)
        self.incoming_connections.on_changed.add_handler(self._updated)

        self.outgoing_connections = ConnectionList(OutgoingProtocol)
        self.outgoing_connections.on_changed.add_handler(self._updated)

    @property
    def all_connections(self):
        """Returns an iterator of all current connections"""

        return itertools.chain(self.incoming_connections,
                               self.outgoing_connections)

    def connection_allowed(self, peer_id):
        """
        Returns true if a connection with a peer is allowed.

        :param peer_id: The ID of the peer to check.
        """

        if peer_id in self._connection_attempts:
            logging.info('Connection attempt not allowed with ' + peer_id)
            logging.info(str(self._connection_attempts))

        return (peer_id not in self._connections_ids and
                peer_id not in self._connection_attempts)

    def listen(self, port):
        """Starts listening on the given port."""

        factory = self._create_server_factory()
        reactor.listenTCP(port, factory)

    def get_connection(self, partner_id):
        if partner_id in self.incoming_connections:
            return self.incoming_connections[partner_id]

        if partner_id in self.outgoing_connections:
            return self.outgoing_connections[partner_id]

        return None

    def connect_to_peer(self, peer):
        """Establish a new connection with a given peer."""

        logging.debug('Connecting to peer:' + peer.id)
        self._connection_attempts.add(peer.id)
        factory = self._create_client_factory(peer.id)
        reactor.connectTCP(peer.ip, peer.port, factory)

    def connect_to_peers(self, peers):
        """
        Connect to a list of peers
        """

        for peer in peers:
            if peer.id in self._connections_ids:
                continue
            self.connect_to_peer(peer)

    @property
    def _connections_ids(self):

        return set(self.incoming_connections.ids +
                   self.outgoing_connections.ids)

    def _create_server_factory(self):

        factory = ServerFactory()
        factory.protocol = IncomingProtocol
        factory.add_connection = self.incoming_connections.add
        factory.remove_connection = self.incoming_connections.remove
        self._init_factory(factory)
        return factory

    def _create_client_factory(self, target_id):

        factory = ClientFactory()
        factory.protocol = OutgoingProtocol
        factory.target_id = target_id
        factory.add_connection = self.outgoing_connections.add
        factory.remove_connection = self.outgoing_connections.remove
        self._init_factory(factory)
        return factory

    def _init_factory(self, factory):
        factory.peer_service = self._peer_service
        factory.connection_allowed = self.connection_allowed
        factory.end_connection_attempt = self._end_connection_attempt

    def _updated(self, connection):
        self.on_update.call(self)

    def _end_connection_attempt(self, peer_id):
        if peer_id in self._connection_attempts:
            self._connection_attempts.remove(peer_id)
