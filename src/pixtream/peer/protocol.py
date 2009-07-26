"""
Defines classes for the the Pixtream Protocol
"""

import logging

from twisted.protocols.basic import Int32StringReceiver

from pixtream.peer.messages import HandshakeMessage, Message
from pixtream.peer.messages import MessageDecodingError

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

        try:
            message_object = Message.decode(message)
        except MessageDecodingError as error:
            logging.error('Decoding error ' + str(error))
            self.drop()
            return

        if isinstance(message_object, HandshakeMessage):
            self.receive_handshake(message_object)

    def send_message_object(self, message_object):
        """Sends a message object to the partner peer"""

        message = message_object.prefix_encode()
        self.transport.write(message)

    def send_hanshake(self):
        """Sends a handshake message"""

        logging.debug('Sending Handshake to ' + self.partner_name)
        msg = HandshakeMessage(self.factory.peer_id)
        self.send_message_object(msg)
        self.outgoing_handshaked = True

    def check_incoming_handshake(self, msg):
        """Checks if a received handshake message object is valid"""

        if self.incoming_handshaked:
            logging.error('Double handshake from id ' + self.partner_id)
            return False

        if not msg.validate():
            logging.error('Wrong handshake. Closing connection')
            self.drop()
            return False

        if not self.factory.allow_connection(msg.peer_id):
            logging.error('Connection not allowed with ' + msg.peer_id)
            self.drop()
            return False
        return True

    def receive_handshake(self, msg):
        """Handler for a handshake message"""

        logging.debug('Handshake received from ' + self.partner_name)

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
