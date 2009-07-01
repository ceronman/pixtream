import logging

from twisted.protocols.basic import Int32StringReceiver

from pixtream.peer.messages import HandshakeMessage, Message
from pixtream.peer.messages import MessageDecodingError

class PixtreamProtocol(Int32StringReceiver):

    def __init__(self, peer_id):
        self.peer_id = peer_id
        self.other_id = None
        self.handshaked = False

    def connectionMade(self):
        logging.debug('Connection made {0}'.format(self.peer_id))

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
        if (msg.validate() and self.factory.allow_connection(msg.peer_id)):
                self.other_id = msg.peer_id
                self.factory.add_connection(self)
                self.send_hanshake()
                self.handshaked = True
        else:
            self.transport.loseConnection()
