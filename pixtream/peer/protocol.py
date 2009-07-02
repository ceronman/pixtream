import logging

from twisted.protocols.basic import Int32StringReceiver

from pixtream.peer.messages import HandshakeMessage, Message
from pixtream.peer.messages import MessageDecodingError

class PixtreamProtocol(Int32StringReceiver):

    def __init__(self):
        self.other_id = None
        self.handshaked = False

    @property
    def peer_id(self):
        return self.factory.peer_id

    def connectionMade(self):
        logging.debug('Connection made {0}'.format(self.peer_id))
        if self.other_id is not None:
            self.send_hanshake()

    def connectionLost(self, reason):
        logging.debug('Connection lost {0}. Reason: {1}'.format(self.peer_id,
                                                                reason))
        self.factory.remove_connection(self)

    def stringReceived(self, message):
        logging.debug('Received message: ' + repr(message))

        try:
            message_object = Message.decode(message)
        except MessageDecodingError as error:
            logging.error(str(error))
            self.transport.loseConnection()
            return

        if isinstance(message_object, HandshakeMessage):
            self.receive_handshake(message_object)

    def send_message_object(self, message_object):
        message = message_object.prefix_encode()
        self.transport.write(message)

    def send_hanshake(self):
        logging.debug('Sending Handshake')
        msg = HandshakeMessage(self.factory.peer_id)
        self.send_message_object(msg)

    def receive_handshake(self, msg):
        logging.debug('Handshake received')

        if not msg.validate():
            logging.error('Wrong handshake. Closing connection')
            self.drop()
            return

        if not self.factory.allow_connection(msg.peer_id):
            logging.error('Connection not allowed with ' + msg.peer_id)
            self.drop()
            return

        if not self.verify_peer(msg.peer_id):
            logging.error('Expected a different peer ' + msg.peer_id)
            self.drop()
            return

        logging.debug('Good handshake ' + msg.peer_id)
        self.other_id = msg.peer_id
        self.factory.add_connection(self)
        self.send_hanshake()
        self.handshaked = True

    def verify_peer(self, peer_id):
        if self.factory.target__id is not None:
            return peer_id == self.factory.target_id

    def drop(self):
        self.loseConnection()

