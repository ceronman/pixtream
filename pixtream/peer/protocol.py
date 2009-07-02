import logging

from twisted.protocols.basic import Int32StringReceiver

from pixtream.peer.messages import HandshakeMessage, Message
from pixtream.peer.messages import MessageDecodingError

class BaseProtocol(Int32StringReceiver):

    def __init__(self):
        self.partner_id = None
        self.outgoing_handshaked = False
        self.incoming_handshaked = False

    @property
    def handshaked(self):
        return self.outgoing_handshaked and self.incoming_handshaked

    @property
    def partner_name(self):
        return str(self.transport.getPeer())

    def stringReceived(self, message):
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
        message = message_object.prefix_encode()
        self.transport.write(message)

    def send_hanshake(self):
        logging.debug('Sending Handshake to ' + self.partner_name)
        msg = HandshakeMessage(self.factory.peer_id)
        self.send_message_object(msg)
        self.outgoing_handshaked = True

    def check_incoming_handshake(self, msg):
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

class IncomingProtocol(BaseProtocol):
    def connectionMade(self):
        logging.debug('Incoming connection made: ' + self.partner_name)

    def connectionLost(self, reason):
        logging.debug('Incoming connection lost: ' + str(reason))

        if self.handshaked:
            self.factory.remove_incoming_connection(self)

    def receive_handshake(self, msg):
        logging.debug('Handshake received from ' + self.partner_name)

        if not self.check_incoming_handshake(msg):
            return

        logging.debug('Good handshake ' + msg.peer_id)

        self.partner_id = msg.peer_id
        self.send_hanshake()
        self.factory.add_incoming_connection(self)

        self.incoming_handshaked = True

    def drop(self):
        self.transport.loseConnection()

class OutgoingProtocol(BaseProtocol):

    def connectionMade(self):
        logging.debug('Outgoing connection made ' + self.partner_name)
        self.send_hanshake()

    def connectionLost(self, reason):
        logging.debug('Incoming connection lost' + str(reason))
        if self.handshaked:
            self.factory.remove_outgoing_connection(self)
        self.drop()

    def receive_handshake(self, msg):
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
        self.factory.add_outgoing_connection(self)

        self.incoming_handshaked = True

    def drop(self):
        self.transport.loseConnection()

