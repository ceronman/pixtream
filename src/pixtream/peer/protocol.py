"""
Defines classes for the the Pixtream Protocol
"""

import logging

from twisted.protocols.basic import Int32StringReceiver

from pixtream.peer.messages import Message, MessageException
from pixtream.peer import specs

class BaseProtocol(Int32StringReceiver):
    """
    Base class for the procols of Pixtream

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

    @property
    def handshaked(self):
        """True if both peers of the connections has send a proper handshake"""

        return self.outgoing_handshaked and self.incoming_handshaked

    @property
    def partner_name(self):
        """Returns the IP address of the partner peer"""

        return str(self.transport.getPeer())

    def connectionMade(self):
        logging.debug('Connection made ' + self.partner_name)

    def connectionLost(self, reason):
        msg = 'Connection lost: ({0}) ({1})'
        msg = msg.format(self.partner_name, str(reason))
        logging.debug(msg)

        if self.handshaked:
            self.factory.remove_connection(self)

    def stringReceived(self, message):
        """Overrides method to receive a message without the prefix """

        logging.debug('Received: {0} from {1}'.format(repr(message),
                                                      self.partner_name))

        # if we have hands
        if self.handshaked and self.choked:
            logging.info('Ignoring message because the peer is choked')
            return

        try:
            message_object = Message.parse(message)
        except MessageException as error:
            logging.error('Decoding error ' + str(error))
            self.drop()
            return

        if isinstance(message_object, specs.HandshakeMessage):
            self.receive_handshake(message_object)
            return

        if not self.handshaked:
            logging.error('Received a message before handshake')
            self.drop()

        if isinstance(message_object, specs.ChokeMessage):
            self.partner_choked = True
            return

        if isinstance(message_object, specs.UnChokeMessage):
            self.partner_choked = False
            return

        if isinstance(message_object, specs.InterestedMessage):
            self.partner_interested = True
            return

        if isinstance(message_object, specs.NotInterestedMessage):
            self.partner_interested = False
            return

        if isinstance(message_object, specs.HeartBeatMessage):
            return

        if isinstance(message_object, specs.PieceBitFieldMessage):
            self.partner_pieces = message_object.pieces
            return

        if isinstance(message_object, specs.GotPieceMessage):
            self.partner_pieces.add(message_object.sequence)
            logging.debug('Got piece {0}', message_object.sequence)
            return

    def send_message(self, message_class, *args, **kwargs):
        """Sends a message object to the partner peer"""

        message_object = message_class.create(*args, **kwargs)
        self.transport.write(message_object.prefix_encode)

    def send_hanshake(self):
        """Sends a handshake message"""

        logging.debug('Sending Handshake to ' + self.partner_name)

        self.send_message(specs.HandshakeMessage, self.factory.peer_id)
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
        pieces = self.factory.get_sequences()
        self.send_message(specs.NotInterestedMessage, pieces)

    def send_got_piece(self, sequence):
        self.send_message(specs.GotPieceMessage, sequence)

    def check_incoming_handshake(self, msg):
        """Checks if a received handshake message object is valid"""

        if self.incoming_handshaked:
            logging.error('Double handshake from id ' + self.partner_id)
            return False

        if not msg.is_valid():
            logging.error('Wrong handshake. Closing connection')
            self.drop()
            return False

        if not self.factory.allow_connection(msg.peer_id):
            logging.error('Connection not allowed with ' + msg.peer_id)
            self.drop()
            return False
        return True

    def drop(self):
        """Drops the connection"""
        self.transport.loseConnection()

class IncomingProtocol(BaseProtocol):
    """
    Protocol for incoming connections.
    """

    def receive_handshake(self, msg):
        """Handler for a handshake message"""

        logging.debug('Handshake received from ' + self.partner_name)

        if not self.check_incoming_handshake(msg):
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
        self.send_hanshake()

    def receive_handshake(self, msg):
        """Handler for a received handshake message object"""

        logging.debug('Handshake received from ' + self.partner_name)

        if not self.check_incoming_handshake(msg):
            return

        if not self.outgoing_handshaked:
            logging.error('Unrequested handshake from ' + self.partner_name)
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
