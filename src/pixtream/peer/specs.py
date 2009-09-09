"""
Message specs of the Pixtream protocol
"""

import math

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
        assert len(peer_id) == 20
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

@Message.register
class RequestDataPacketMessage(FixedLengthMessage):
    """
    Used by peers to request a data packet
    """

    message_header = 'Q'

    fields = [
        Field('I', 'sequence',
              """Sequence of the piece requested""")
    ]

    def valid_conditions(self):
        yield self.sequence >= 0

    @classmethod
    def create(cls, sequence):
        assert sequence >= 0

        msg = cls()
        msg.sequence = sequence
        return msg

@Message.register
class CancelRequestDataPacketMessage(FixedLengthMessage):
    """
    Cancel a previous request of a data packet
    """

    message_header = 'X'

    fields = [
        Field('I', 'sequence',
              """Sequence of the piece to be canceled""")
    ]

    def valid_conditions(self):
        yield self.sequence >= 0

@Message.register
class HeartBeatMessage(FixedLengthMessage):
    """
    Heart Beat Message to keep alive a connection

    Is used by peers to keep connections. In a connection, if a Peer has not
    received a heart beat message within N seconds, the connection is dropped.
    N is defined by the Peer's connection mannager.
    """

    message_header = 'B'
    fields = []

@Message.register
class ChokeMessage(FixedLengthMessage):
    """
    Message to choke other peer
    """

    message_header = 'C'
    fields = []

@Message.register
class UnChokeMessage(FixedLengthMessage):
    """
    Message to unchoke other peer
    """

    message_header = 'U'
    fields = []

@Message.register
class InterestedMessage(FixedLengthMessage):
    """
    Message to tell other peers we are interested
    """

    message_header = 'I'
    fields = []

@Message.register
class NotInterestedMessage(FixedLengthMessage):
    """
    Message to tell other peers we are not interested
    """

    message_header = 'N'
    fields = []

@Message.register
class GotPieceMessage(FixedLengthMessage):
    """
    Message to tell other peers we got a piece
    """

    message_header = 'G'

    fields = [
        Field('I', 'sequence',
              """Sequence of the piece gotten""")
    ]

    @classmethod
    def create(cls, sequence):
        assert sequence >= 0

        msg = cls()
        msg.sequence = sequence
        return msg

    def valid_conditions(self):
        yield self.sequence >= 0

@Message.register
class PieceBitFieldMessage(VariableLengthMessage):
    """
    Message containing a bit field of the available pieces of a peer
    """

    message_header = 'F'

    fields = [
        Field('I', 'first_sequence',
              """The sequence where the bit field is starting"""),

        Field('I', 'last_sequence',
              """The sequence of the last bit in the bit field""")
    ]

    payload = Payload("""The bit field""")

    def valid_conditions(self):
        yield self.first_sequence >= 0
        yield self.last_sequence >= 0

    @classmethod
    def create(cls, pieces):
        assert isinstance(pieces, set)

        msg = cls()
        first, last, bitfield = cls._encode_bitfield(pieces)
        msg.first_sequence = first
        msg.last_sequence = last
        msg.bitfield = bitfield

        return msg

    def unpack_payload(self, payload):
        self.bitfield = payload
        self.pieces = self._decode_bitfield(self.first_sequence, self.bitfield)

    def pack_payload(self):
        return self.bitfield

    @staticmethod
    def _encode_bitfield(pieces):
        if len(pieces) == 0:
            return 0, 0, ''

        first = min(pieces)
        last = max(pieces)

        byte = ''
        bitfield = ''
        for piece in range(first, last+1):
            bit = '1' if piece in pieces else '0'
            byte += bit
            if len(byte) == 8:
                bitfield += chr(int(byte, 2))
                byte = ''
        if len(byte) > 0:
            byte += (8 - len(byte))*'0'
            bitfield += chr(int(byte, 2))

        return first, last, bitfield

    @staticmethod
    def _decode_bitfield(first, bitfield):
        bitstr = ''.join(format(ord(char), '0>8b') for char in bitfield)
        return set(first + i for i, bit in enumerate(bitstr) if bit == '1')

@Message.register
class RequestPieceBitFieldMessage(FixedLengthMessage):
    """
    Message to request a peer for its piece bit field
    """

    message_header = 'R'
    fields = []




