import logging

from pixtream.peer.protocol import PixtreamProtocol
from pixtream.util.twistedrepeater import TwistedRepeater

CHECK_INTERVAL = 10

class ConnectionManager(object):

    def __init__(self, peer_service):
        self._peer_service = peer_service
        self._active_connections = {}
        self._checker_repeater = TwistedRepeater(self.check_connections,
                                                 CHECK_INTERVAL)
        self._checker_repeater.start_later()


    def add_connection(self, connection):
        assert isinstance(connection, PixtreamProtocol)
        assert hasattr(connection, 'other_id')
        assert isinstance(connection.other_id, str)

        self._active_connections[connection.other_id] = connection

    def remove_connection(self, connection):
        assert isinstance(connection, PixtreamProtocol)
        assert hasattr(connection, 'other_id')
        assert isinstance(connection.other_id, str)

        self._active_connections.pop(connection.other_id, None)

    def allow_connection(self, peer_id):
        return peer_id not in self._active_connections

    def check_connections(self):
        connections = self._active_connections.keys()
        logging.debug('Active connections ' + str(connections))

