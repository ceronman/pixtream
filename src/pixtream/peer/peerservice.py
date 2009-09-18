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
from pixtream.util.twistedrepeater import TwistedRepeater

__all__ = ['PeerService', 'SourcePeerService']

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

        # FIXME: seconds hardcoded
        self.logic_repeater = TwistedRepeater(self._peer_logic, 2)
        self.logic_repeater.start_later()

    @property
    def pieces(self):
        return self.piece_manager.piece_sequences

    def partner_got_piece(self, partner_id, piece):
        self.piece_manager.partner_got_piece(partner_id, piece)

    def partner_bitset(self, partner_id, pieces):
        self.piece_manager.partner_got_pieces(partner_id, pieces)

    def receive_request(self, partner_id, sequence):
        if self.piece_manager.piece_sent_allowed(partner_id, sequence):
            logging.info('Sent Allowed')
            data = self.piece_manager.get_piece_data(sequence)
            if data is None:
                logging.error('Getting None data in piece manager')
                return
            connection = self.connection_manager.get_connection(partner_id)
            if connection == None:
                logging.error('Getting None in connection manager')
                return
            connection.send_data_packet(sequence, data)
            self.piece_manager.piece_sent(partner_id, sequence)
        else:
            logging.info("Sent NOT Allowed")

    def receive_packet(self, packet):
        self.joiner.push_packet(packet)
        self.piece_manager.got_new_piece(packet.sequence, packet.data)
        for connection in self.connection_manager.all_connections:
            connection.send_got_piece(packet.sequence)

    def _peer_logic(self):
        logging.info('Executing Repeater')
        self._contact_peers(self.tracker_peers)

        # FIXME: hardcoded number!!!
        missing_pieces = self.piece_manager.most_wanted_pieces(3)

        for piece in missing_pieces:
            partner_id = self.piece_manager.best_partner_for_piece(piece)
            if partner_id is None:
                logging.info('No partner for {0}'.format(piece))
                continue
            connection = self.connection_manager.get_connection(partner_id)
            if connection is None:
                logging.error('No connection for {0}'.format(partner_id))
                continue

            if self.piece_manager.piece_request_allowed(partner_id, piece):
                connection.send_request_packet(piece)
                self.piece_manager.piece_requested(partner_id, piece)

    def _update_peers(self, sender, peer_list):
        self.tracker_peers.update_peers(peer_list)
        self.tracker_peers.remove_peer(self.peer_id)
        logging.debug('Tracker updated: ' + str(self.tracker_peers.peer_ids))

    def _contact_peers(self, peers):
        self.connection_manager.connect_to_peers(peers)

    def _data_joined(self, joiner):
        self.stream_server.send_stream(joiner.pop_stream())

    def _create_piece_manager(self):
        self.piece_manager = PieceManager()

    def _create_connection_manager(self):
        self.connection_manager = ConnectionManager(self)

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

    def _peer_logic(self):
        pass

    def _packet_created(self, splitter):
        packet = splitter.pop_packet()
        self.receive_packet(packet)
        logging.debug('Packet created. Seq: {0}'.format(packet.sequence))

    def _input_stream_end(self, splitter):
        self.joiner.end_join()

    def _create_splitter(self):
        self.splitter = Splitter(SPLIT_PACKET_SIZE)
        self.splitter.on_new_packet.add_handler(self._packet_created)
        self.splitter.on_stream_end.add_handler(self._input_stream_end)

    def _create_stream_client(self):
        self.stream_client = TCPStreamClient(self.splitter)
