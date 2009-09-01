"""
Controls the peer application

It manages the Tracker Manager and the Connection Manager
"""

import logging
import uuid

from pixtream.peer.piecemanager import PieceManager
from pixtream.peer.trackermanager import TrackerManager
from pixtream.peer.connectionmanager import ConnectionManager
from pixtream.peer.joiner import Joiner
from pixtream.peer.splitter import Splitter
from pixtream.peer.streamserver import TCPStreamServer
from pixtream.peer.streamclient import TCPStreamClient
from pixtream.peer.peerdatabase import PeerDatabase
from pixtream.util.event import Event

class PeerService(object):
    """
    Controls every aspect of the peer application.
    """

    # TODO: Refactor this. Use specific methods.
    def __init__(self, ip, port, tracker_url, streaming_port):
        """
        Inits the Peer application.

        :param ip: The IP address of the peer.
        :param port: The port to listen.
        :param tracker_url: The URL of the tracker.
        """

        self.port = port
        self.ip = ip

        self.peer_id = self._generate_peer_id()
        self.tracker_peers = PeerDatabase()
        self.own_pieces = set()
        self.pieces_by_partner = {}

        self.piece_manager = None
        self.connection_manager = None
        self.tracker_manager = None
        self.joiner = None
        self.stream_server = None

        self._create_piece_manager()
        self._create_connection_manager()
        self._create_tracker_manager(tracker_url)
        self._create_joiner()
        self._create_stream_server(streaming_port)

        self.on_tracker_update = Event()
        self.on_peers_update = Event()

    @property
    def incoming_peers(self):
        """Returns a list of the IDs of the incomming connected peers"""
        return self.connection_manager.incoming_connections.ids

    @property
    def outgoing_peers(self):
        """Returns a list of the IDs of the incomming connected peers"""
        return self.connection_manager.outgoing_connections.ids

    @property
    def pieces(self):
        return self.piece_manager.own_pieces

    def partner_got_piece(self, partner_id, piece):
        self.piece_manager.partner_got_piece(partner_id, piece)

    def partner_got_pieces(self, partner_id, pieces):
        self.piece_manager.partner_got_pieces(partner_id, pieces)

    def listen(self):
        """Starts listening on the selected port"""
        self.connection_manager.listen(self.port)

    def connect_to_tracker(self):
        """Contact the tracker for first time"""
        self.tracker_manager.connect_to_tracker()

    def _update_peers(self, sender, peer_list):
        self.tracker_peers.update_peers(peer_list)
        self.tracker_peers.remove_peer(self.peer_id)
        logging.debug('Tracker updated: ' + str(self.tracker_peers.peer_ids))
        self._contact_peers(self.tracker_peers)
        self.on_tracker_update.call(self)

    def _update_connections(self, sender):
        self.on_peers_update.call(self)

    def _contact_peers(self, peers):
        self.connection_manager.connect_to_peers(peers)

    def _data_packet_arrived(self, packet):
        self.joiner.push_packet(packet)
        self.piece_manager.got_new_piece(packet.sequence)
        for connection in self.connection_manager.all_connections:
            connection.send_got_piece(packet.sequence)

    def _data_joined(self, joiner):
        self.stream_server.send_stream(joiner.pop_stream())

    def _create_piece_manager(self):
        self.piece_manager = PieceManager()

    def _create_connection_manager(self):
        self.connection_manager = ConnectionManager(self)
        self.connection_manager.on_update.add_handler(self._update_connections)

    def _create_tracker_manager(self, tracker_url):
        self.tracker_manager = TrackerManager(self.peer_id,
                                              self.ip,
                                              self.port,
                                              tracker_url)

        self.tracker_manager.on_updated.add_handler(self._update_peers)

    def _create_joiner(self):
        self.joiner = Joiner()
        self.joiner.on_data_joined.add_handler(self._data_joined)

    def _create_stream_server(self, streaming_port):
        self.stream_server = TCPStreamServer(streaming_port)
        self.stream_server.listen()

    def _generate_peer_id(self):
        id = uuid.uuid4().hex
        id = id[:14]
        ## TESTING
        id = format(self.port, '014d')
        ## END TESTING
        peer_id = 'PX0001' +  id
        logging.debug('Generated Peer ID: "{0}"'.format(peer_id))
        return peer_id

# TODO: Move this to a config based system
SPLIT_PACKET_SIZE = 64000

class SourcePeerService(PeerService):

    def __init__(self, ip, port, tracker_url, streaming_port):
        super(SourcePeerService, self).__init__(ip, port,
                                                tracker_url, streaming_port)

        self.splitter = None
        self.stream_client  = None

        self._create_splitter()
        self._create_stream_client()

    def connect_to_source(self, host, port):
        self.stream_client.connect(host, port)

    def _packet_created(self, splitter):
        packet = splitter.pop_packet()
        self._data_packet_arrived(packet)
        logging.debug('Packet created. Seq: {0}'.format(packet.sequence))

    def _input_stream_end(self, splitter):
        self.joiner.end_join()

    def _create_splitter(self):
        self.splitter = Splitter(SPLIT_PACKET_SIZE)
        self.splitter.on_new_packet.add_handler(self._packet_created)
        self.splitter.on_stream_end.add_handler(self._input_stream_end)

    def _create_stream_client(self):
        self.stream_client = TCPStreamClient(self.splitter)
