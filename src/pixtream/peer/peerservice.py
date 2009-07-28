"""
Controls the peer application

It manages the Tracker Manager and the Connection Manager
"""

import logging
from uuid import uuid4

from pixtream.peer.trackermanager import TrackerManager
from pixtream.peer.peerdatabase import PeerDatabase
from pixtream.peer.connectionmanager import ConnectionManager
from pixtream.peer.joiner import Joiner
from pixtream.peer.splitter import Splitter
from pixtream.peer.streamserver import TCPStreamServer
from pixtream.peer.streamclient import TCPStreamClient
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

        self.peer_id = None
        self.connection_manager = None
        self.tracker_manager = None
        self.joiner = None
        self.stream_server = None

        self._generate_peer_id()
        self._create_connection_manager()
        self._create_tracker_manager(tracker_url)
        self._create_joiner()
        self._create_stream_server(streaming_port)

        self.available_peers = PeerDatabase()
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

    def listen(self):
        """Starts listening on the selected port"""
        self.connection_manager.listen()

    def connect_to_tracker(self):
        """Contact the tracker for first time"""
        self.tracker_manager.connect_to_tracker()

    def _update_peers(self, sender, peer_list):
        """Hander to be called when the tracker is updated"""
        self.available_peers.update_peers(peer_list)
        self.available_peers.remove_peer(self.peer_id)
        logging.debug('Tracker updated: ' + str(self.available_peers.peer_ids))
        self.on_tracker_update.call(self)

    def _update_connections(self, sender):
        self.on_peers_update.call(self)

    def _data_packet_arrived(self, packet):
        self.joiner.push_packet(packet)
        self.connection_manager.announce_packet(packet.sequence)

    def _data_joined(self, joiner):
        self.stream_server.send_stream(joiner.pop_stream())

    def _generate_peer_id(self):
        id = uuid4().hex
        id = id[:14]
        self.peer_id = 'PX0001' +  id

    def _create_connection_manager(self):
        self.connection_manager = ConnectionManager(self)
        self.connection_manager.on_update.add_handler(self._update_connections)

    def _create_tracker_manager(self, tracker_url):
        self.tracker_manager = TrackerManager(self, tracker_url)
        self.tracker_manager.on_updated.add_handler(self._update_peers)

    def _create_joiner(self):
        self.joiner = Joiner()
        self.joiner.on_data_joined.add_handler(self._data_joined)

    def _create_stream_server(self, streaming_port):
        self.stream_server = TCPStreamServer(streaming_port)
        self.stream_server.listen()

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
