from twisted.internet import protocol

from pixtream.peer.protocol import PixtreamProtocol

class ServerFactory(protocol.ServerFactory):

    protocol = PixtreamProtocol

    def __init__(self, peer_service):
        self._peer_service = peer_service

        cm = peer_service.connection_manager

        self.add_connection = cm.add_connection
        self.remove_connection = cm.remove_connection
        self.allow_connection = cm.allow_connection

    @property
    def peer_id(self):
        return self._peer_service.peer_id

    def buildProtocol(self, addr):
        protocol = PixtreamProtocol(self.peer_id)
        protocol.factory = self
        return protocol


