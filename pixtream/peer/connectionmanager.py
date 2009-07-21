"""
Manages incoming and outgoing connections to other peers.
"""

import logging

from twisted.internet.protocol import ServerFactory, ClientFactory
from twisted.internet import reactor

from pixtream.peer.protocol import IncomingProtocol, OutgoingProtocol
from pixtream.util.twistedrepeater import TwistedRepeater
from pixtream.util.event import Event
from pixtream.peer.peerdatabase import Peer

# Configuration constants
# TODO: Use a configuration method instead of this constants
CHECK_INTERVAL = 5

class ConnectionList(object):

    def __init__(self, protocol_class, manager):
        self.on_changed = Event()
        self._connections = {}
        self._protocol_class = protocol_class
        self._manager = manager

    def add(self, connection):
        """Adds a new item to the list of connections."""

        assert isinstance(connection, self._protocol_class)
        assert isinstance(connection.partner_id, str)

        if connection.partner_id in self._connections:
            logging.error('Adding existent connection')
            connection.drop()
            return

        self._connections[connection.partner_id] = connection
        self.on_changed.call(self._manager)

    def remove(self, connection):
        """Removes an item from the list of connections."""

        assert isinstance(connection, self._protocol_class)
        assert isinstance(connection.partner_id, str)

        if connection.partner_id not in self._connections:
            logging.error('Removing nonexistent connection')
            return

        del self._connections[connection.partner_id]
        self.on_changed.call(self._manager)

    @property
    def ids(self):
        return self._connections.keys()

class ConnectionManager(object):
    """
    Maintains a collection of incoming and outgoing connections to a peer.

    The ConnectionManager creates twisted factories for incoming and outgoing
    connections. Uses the twisted reactor to listen on the Peer port and create
    new connections to other peers. It checks the available peers every N
    seconds and generates new connections if is necessary.
    """

    def __init__(self, peer_service):
        """
        Creates a new ConnectionManager object.

        :param peer_service: The parent peer service.
        """
        self.on_update = Event()

        self.incoming_connections = ConnectionList(IncomingProtocol, self)
        self.outgoing_connections = ConnectionList(OutgoingProtocol, self)

        self.incoming_connections.on_changed.add_handler(self.on_update.call)
        self.outgoing_connections.on_changed.add_handler(self.on_update.call)

        self._peer_service = peer_service
        self._checker_repeater = TwistedRepeater(self.check_connections,
                                                 CHECK_INTERVAL)
        self._checker_repeater.start_later()

    @property
    def contacted_peers(self):
        """Returns the IDs of all peers currently contacted."""

        return set(self.incoming_connections.ids +
                   self.outgoing_connections.ids)

    def create_server_factory(self):
        """Returns a newly created server factory for a peer."""

        factory = ServerFactory()
        factory.protocol = IncomingProtocol
        factory.peer_id = self._peer_service.peer_id
        factory.add_connection = self.incoming_connections.add
        factory.remove_connection = self.incoming_connections.remove
        factory.allow_connection = self.allow_connection

        return factory

    def create_client_factory(self, target_id):
        """Returns a newly created server factory for a peer."""

        factory = ClientFactory()
        factory.protocol = OutgoingProtocol
        factory.peer_id = self._peer_service.peer_id
        factory.target_id = target_id
        factory.add_connection = self.outgoing_connections.add
        factory.remove_connection = self.outgoing_connections.remove
        factory.allow_connection = self.allow_connection

        return factory

    def allow_connection(self, peer_id):
        """
        Returns true if a connection with a peer is allowed.

        :param peer_id: The ID of the peer to check.
        """

        return peer_id not in self.contacted_peers

    def check_connections(self):
        """
        Checks current connections.

        Checks the state of current connections and establish new connections
        with know peers.
        """

        self._contact_peers()

    def listen(self):
        """Starts listening on the peer port."""

        factory = self.create_server_factory()
        reactor.listenTCP(self._peer_service.port, factory)

    def connect_to_peer(self, peer):
        """Establish a new connection with a given peer."""

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
