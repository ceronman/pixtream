"""
Message specs of the Pixtream protocol
"""

from pixtream.peer.messages import FixedLengthMessage, VariableLengthMessage
from pixtream.peer.messages import Message, Field, Payload

@Message.register
class HandshakeMessage(FixedLengthMessage):
    """
    The first message send when two peers connect each other
    """

    message_header = 'H'

    fields = [
        Field('17s', 'protocol_id',
             """'Pixtream Protocol' string"""),

        Field('8s', 'extensions',
              """Reserved for future extensions"""),

        Field('20s', 'peer_id',
              """Unique ID of the peer"""),
    ]

    def valid_conditions(self):
        yield self.protocol_id == 'Pixtream Protocol'
        yield len(self.peer_id) == 20

    @classmethod
    def create(cls, peer_id):
        assert isinstance(peer_id, str)
        msg = cls()
        msg.peer_id = peer_id
        msg.protocol_id = 'Pixtream Protocol'
        msg.extensions = '00000000'
        return msg


@Message.register
class DataPacketMessage(VariableLengthMessage):
    """
    Message containing a part of a stream
    """

    message_header = 'D'

    fields = [
        Field('I', 'sequence',
              """Sequence number of the packet in the stream""")
    ]

    payload = Payload("""Data bytes of the packet""")

    def valid_conditions(self):
        yield self.sequence >= 0

    @classmethod
    def create(cls, sequence, data):
        assert sequence >= 0
        msg = cls()
        msg.sequence = sequence
        msg.data = data
        return msg

    def unpack_payload(self, payload):
        self.data = payload

    def pack_payload(self):
        return self.data
