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
from pixtream.peer.utilitymanager import UtilityManager
from pixtream.peer.peerdatabase import PeerDatabase, Peer
from pixtream.util.twistedrepeater import TwistedRepeater

__all__ = ['PeerService', 'SourcePeerService']

class PeerService(object):
    """
    Controls every aspect of the peer application.
    """

    # TODO: Refactor this. Use specific methods.
    def __init__(self, ip, port, tracker_url):
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
        self._create_utility_manager()
        self._create_connection_manager()
        self._create_tracker_manager(tracker_url)
        self._create_joiner()

        # FIXME: seconds hardcoded
        self.logic_repeater = TwistedRepeater(self._peer_logic, 2)
        self.logic_repeater.start_later()

    @property
    def pieces(self):
        return self.piece_manager.own_sequences

    def partner_got_piece(self, partner_id, piece):
        self.piece_manager.partner_got_piece(partner_id, piece)

    def partner_bitset(self, partner_id, pieces):
        self.piece_manager.partner_got_pieces(partner_id, pieces)

    def receive_request(self, partner_id, sequence):
        self.piece_manager.partner_requested_piece(partner_id, sequence)

    def receive_packet(self, packet, sender_id):
        self.joiner.push_packet(packet)
        self.piece_manager.add_new_piece(packet.sequence, packet.data)
        if sender_id is not None:
            self.utility_manager.add_peer_utility(sender_id, len(packet.data))

        for connection in self.connection_manager.all_connections:
            connection.send_got_piece(packet.sequence)

    def _peer_logic(self):
        logging.info('Executing Peer Logic')
        self._refresh_connections()
        self._contact_peers(self.tracker_peers)
        self._request_needed_pieces()
        self._send_requested_pieces()

        utility = self.utility_manager.utility_by_peer
        self.tracker_manager.utility_by_peer.update(utility)

    def _request_needed_pieces(self):

        missing_pieces = self.piece_manager.get_pieces_to_request()

        for piece in missing_pieces:
            partner_id = self.piece_manager.best_partner_for_piece(piece)
            if partner_id is None:
                logging.error('No partner for {0}'.format(piece))
                continue
            connection = self.connection_manager.get_connection(partner_id)
            if connection is None:
                logging.error('No connection for {0}'.format(partner_id))
                continue

            if self.piece_manager.can_request_piece(partner_id, piece):
                connection.send_request_packet(piece)
                self.piece_manager.mark_piece_as_requested(partner_id, piece)

    def _send_requested_pieces(self):
        for partner_id, sequence in self.piece_manager.get_pieces_to_send():
            data = self.piece_manager.get_piece_data(sequence)
            if data is None:
                logging.error('Dont have piece {0}'.format(sequence))
                return
            connection = self.connection_manager.get_connection(partner_id)
            if connection == None:
                logging.error('Dont have connection {0}'.format(partner_id))
                return
            connection.send_data_packet(sequence, data)
            self.piece_manager.mark_piece_as_sent(partner_id, sequence)
            logging.info('Sending data {0} to {1}'.format(sequence, partner_id))

    def _update_peers(self, sender, peer_list):
        self.tracker_peers.update_peers(peer_list)
        self.tracker_peers.remove_peer(self.peer_id)

        peers = '|'.join(str(p) for p in self.tracker_manager.peer_list)
        logging.debug('Tracker updated: {0}'.format(peers))

    def _contact_peers(self, peers):
        self.connection_manager.connect_to_peers(peers)

    def _refresh_connections(self):
        self.connection_manager.heartbeat()
        self.connection_manager.check_heartbeats()

    def _data_joined(self, joiner):
        if self.stream_server:
            self.stream_server.send_stream(joiner.pop_stream())
        else:
            logging.debug('Data joined without stream_server')

    def _create_piece_manager(self):
        self.piece_manager = PieceManager()

    def _create_connection_manager(self):
        self.connection_manager = ConnectionManager(self)

    def _create_tracker_manager(self, tracker_url):
        peer = Peer(self.peer_id, self.ip, self.port)
        self.tracker_manager = TrackerManager(tracker_url, peer)

        self.tracker_manager.on_updated.add_handler(self._update_peers)

    def _create_joiner(self):
        self.joiner = Joiner()
        self.joiner.on_data_joined.add_handler(self._data_joined)

    def _create_utility_manager(self):
        self.utility_manager = UtilityManager()

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

    def __init__(self, ip, port, tracker_url):
        super(SourcePeerService, self).__init__(ip, port, tracker_url)

        self.splitter = None
        self.stream_client  = None

        self._create_splitter()

    def _peer_logic(self):
        self._send_requested_pieces()

    def _packet_created(self, splitter):
        packet = splitter.pop_packet()
        self.receive_packet(packet, None)
        logging.debug('Packet created. Seq: {0}'.format(packet.sequence))

    def _input_stream_end(self, splitter):
        self.joiner.end_join()

    def _create_splitter(self):
        self.splitter = Splitter(SPLIT_PACKET_SIZE)
        self.splitter.on_new_packet.add_handler(self._packet_created)
        self.splitter.on_stream_end.add_handler(self._input_stream_end)

    def _stream_received(self, data):
        self.splitter.push_stream(data)

    def _stream_end(self):
        self.splitter.end_stream()

    def attach_stream_client(self, client):
        self.stream_client = client
        client.on_stream_received.add_handler(self._stream_received)
        client.on_stream_end.add_handler(self._stream_end)
