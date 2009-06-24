import logging

from twisted.protocols.basic import Int32StringReceiver

from pixtream.peer.messages import HandshakeMessage, Message
from pixtream.peer.messages import MessageDecodingError

class PixtreamProtocol(Int32StringReceiver):

    def __init__(self, peer_id):
        self.peer_id = peer_id
        self.handshaked = False

    def connectionMade(self):
        logging.debug('Connection Made {0}'.format(self.peer_id))
        self.factory.add_connection(self)

    def connectionLost(self):
        logging.debug('Connection Lost {0}'.format(self.peer_id))
        self.factory.remove_connection(self)

    def stringReceived(self, message):
        logging.debug('Received Message: ' + repr(message))

        try:
            message_object = Message.decode(message)
        except MessageDecodingError as error:
            logging.error(str(error))
            return

        if isinstance(message_object, HandshakeMessage):
            self.receive_handshake(message_object)

    def send_message_object(self, message_object):
        message = message_object.prefix_encode()
        self.transport.write(message)

    def send_hanshake(self):
        handshake = HandshakeMessage(self.factory.peer_id)
        self.send_message_object(handshake)

    def receive_handshake(self, handshake):
        logging.info('Handshake received')
        self.handshaked = True
