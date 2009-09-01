"""
Defines classes for the the Pixtream Protocol
"""

import logging

from twisted.protocols.basic import Int32StringReceiver

from pixtream.peer.messages import Message, MessageException
from pixtream.peer import specs

class BaseProtocol(Int32StringReceiver):
    """
    Base class for the protocols of Pixtream

    It is based on the Int32StringReceiver class of Twister which handles
    int 32 prefixed messages.
    """

    def __init__(self):
        self.partner_id = None
        self.outgoing_handshaked = False
        self.incoming_handshaked = False
        self.choked = True
        self.interested = False
        self.partner_choked = True
        self.partner_interested = False

        self.handlers = {
            specs.HandshakeMessage: self.receive_handshake,
            specs.ChokeMessage: self.receive_choke,
            specs.UnChokeMessage: self.receive_unchoke,
            specs.InterestedMessage: self.receive_interested,
            specs.NotInterestedMessage: self.receive_not_interested,
            specs.HeartBeatMessage: self.receive_heartbeat,
            specs.PieceBitFieldMessage: self.receive_bitfield,
            specs.GotPieceMessage: self.receive_got_piece
        }

    @property
    def peer_service(self):
        return self.factory.peer_service

    @property
    def handshaked(self):
        """True if both peers of the connections has send a proper handshake"""

        return self.outgoing_handshaked and self.incoming_handshaked

    @property
    def partner_address(self):
        """Returns the IP address of the partner peer"""

        return str(self.transport.getPeer())

    def connectionMade(self):
        logging.debug('Connection made ' + self.partner_address)

    def connectionLost(self, reason):
        msg = 'Connection lost: ({0}) ({1})'
        msg = msg.format(self.partner_address, str(reason))
        logging.debug(msg)

        if self.handshaked:
            self.factory.remove_connection(self)

    def stringReceived(self, message):
        """Overrides method to receive a message without the prefix """

        logging.debug('Received: {0} from {1}'.format(repr(message),
                                                      self.partner_address))

        if self.handshaked and self.choked:
            logging.info('Ignoring message because the peer is choked')
            return

        try:
            message_object = Message.parse(message)
        except MessageException as error:
            logging.error('Decoding error ' + str(error))
            self.drop()
            return

        handler = self.handlers.get(type(message_object), self.receive_default)
        handler(message_object)

    def receive_handshake(self, msg):
        pass

    def receive_choke(self, msg):
        self._check_handshaked()
        self.partner_choked = True

    def receive_unchoke(self, msg):
        self._check_handshaked()
        self.partner_choked = False

    def receive_interested(self, msg):
        self._check_handshaked()
        self.partner_interested = True

    def receive_not_interested(self, msg):
        self._check_handshaked()
        self.partner_interested = False

    def receive_bitfield(self, msg):
        self._check_handshaked()
        self.peer_service.partner_got_pieces(self.partner_id, msg.pieces)

    def receive_got_piece(self, msg):
        self._check_handshaked()
        self.peer_service.partner_got_piece(self.partner_id, msg.sequence)
        logging.debug('Got piece {0}'.format(msg.sequence))

    def receive_heartbeat(self, msg):
        self._check_handshaked()

    def receive_default(self, msg):
        logging.error('Received message with no handler ' + str(type(msg)))

    def send_message(self, message_class, *args, **kwargs):
        """Sends a message object to the partner peer"""

        message_object = message_class.create(*args, **kwargs)
        self.transport.write(message_object.pack_prefixed())

    def send_hanshake(self):
        """Sends a handshake message"""

        logging.debug('Sending Handshake to ' + self.partner_address)

        self.send_message(specs.HandshakeMessage, self.peer_service.peer_id)
        self.outgoing_handshaked = True

    def send_choke(self):
        self.send_message(specs.ChokeMessage)
        self.choked = True

    def send_unchoke(self):
        self.send_message(specs.UnChokeMessage)
        self.choked = False

    def send_interested(self):
        self.send_message(specs.InterestedMessage)
        self.interested = True

    def send_not_interested(self):
        self.send_message(specs.NotInterestedMessage)
        self.choked = False

    def send_bitfield(self):
        pieces = self.peer_service.pieces
        self.send_message(specs.PieceBitFieldMessage, pieces)

    def send_got_piece(self, sequence):
        self.send_message(specs.GotPieceMessage, sequence)

    def drop(self):
        """Drops the connection"""
        self.transport.loseConnection()

    def _check_incoming_handshake(self, msg):
        """Checks if a received handshake message object is valid"""

        if self.incoming_handshaked:
            logging.error('Double handshake from id ' + self.partner_id)
            return False

        if not msg.is_valid():
            logging.error('Wrong handshake. Closing connection')
            self.drop()
            return False

        if not self.factory.connection_allowed(msg.peer_id):
            logging.error('Connection not allowed with ' + msg.peer_id)
            self.drop()
            return False
        return True

    def _check_handshaked(self):
        if not self.handshaked:
            logging.error('Received a message before handshake')
            self.drop()

class IncomingProtocol(BaseProtocol):
    """
    Protocol for incoming connections.
    """

    def receive_handshake(self, msg):
        """Handler for a handshake message"""

        logging.debug('Handshake received from ' + self.partner_address)

        if not self._check_incoming_handshake(msg):
            return

        logging.debug('Good handshake ' + msg.peer_id)

        self.partner_id = msg.peer_id
        self.send_hanshake()
        self.factory.add_connection(self)

        self.incoming_handshaked = True
        self.send_unchoke()
        self.send_bitfield()

class OutgoingProtocol(BaseProtocol):
    """
    Protocol for outgoing connection.
    """

    def connectionMade(self):
        BaseProtocol.connectionMade(self)
        self.factory.end_connection_attempt(self.factory.target_id)
        self.send_hanshake()

    def connectionLost(self, reason):
        BaseProtocol.connectionLost(self, reason)
        self.factory.end_connection_attempt(self.factory.target_id)

    def receive_handshake(self, msg):
        """Handler for a received handshake message object"""

        logging.debug('Handshake received from ' + self.partner_address)

        if not self._check_incoming_handshake(msg):
            return

        if not self.outgoing_handshaked:
            logging.error('Unrequested handshake from ' + self.partner_address)
            self.drop()
            return

        if msg.peer_id != self.factory.target_id:
            logging.error('Handshake received from unexpected peer')
            self.drop()
            return

        logging.debug('Good handshake ' + msg.peer_id)

        self.partner_id = msg.peer_id
        self.factory.add_connection(self)

        self.incoming_handshaked = True
        self.send_unchoke()
        self.send_bitfield()
