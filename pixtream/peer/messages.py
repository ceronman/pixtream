"""
Defines Messages Classes for the Pixtream Protocol.

Defines classes for decoding and encoding messages of the Pixtream protocol.
There is one class for each message.
"""

import struct

class MessageDecodingError(Exception):

    """Exception produced during the decoding operation."""

    pass

class Message(object):

    """
    Base class for all messages.

    Can be used to decode new messages and create appropriate objects.
    Subclasses should override validate and encode methods.

    :cvar message_type: One character message type for the class.
    :cvar message_struct: Struct object used to pack the message when encoding.
    """

    _type_map = {}
    _prefix_struct = struct.Struct('!I')
    _type_struct = struct.Struct('!s')

    message_type = '?'
    message_struct = struct.Struct('!s')

    @classmethod
    def register(cls, class_):
        """
        Registers a class message.

        Class decorator to register message classes for a message type.
        This way is possible to use the decode class method to create an object
        of the proper type.
        """

        assert issubclass(class_, Message)
        assert len(class_.message_type) == 1
        assert class_.message_type not in cls._type_map

        cls._type_map[class_.message_type] = class_
        return class_

    @classmethod
    def decode(cls, bytes):
        """
        Decodes a message from a byte string.

        Class method used to decode a message from a byte string.
        It creates an object of the class corresponding to the type registered
        with the register decorator.
        It raises MessageDecodingError exceptions if a message is not well
        formed or a message of an unknown type is received.
        """

        assert len(bytes) > 0

        if len(bytes) < 1:
            raise MessageDecodingError('Decoding empty message')

        message_type = bytes[0]
        message_class = Message._type_map.get(message_type)

        if message_class is None:
            raise MessageDecodingError('Got unregistered message: ' + bytes)

        if message_class is cls:
            raise MessageDecodingError('Can not decode abstract message')

        try:
            return message_class.decode(bytes)
        except struct.error:
            raise MessageDecodingError('Message not well formatted: ' + bytes )


    def encode(self):
        """Encodes the message object and returns a byte string."""

        return self.message_struct.pack(self.message_type)

    def prefix_encode(self):
        """
        Encodes a message with a four bytes integer prefix.

        Similar to encode, but prefixes four bytes with the length of the
        message.
        """

        message = self.encode()
        return Message._prefix_struct.pack(len(message)) + message

    def validate(self):
        """
        Validate if a message contains consistent data.

        Should be overridden in subclasses.
        """
        return True

@Message.register
class HandshakeMessage(Message):
    """
    Message class for the Handshake message of the Pixtream protocol.

    Message description by bytes:
     - Byte  0: One byte for message type. In this case 'H'.
     - Byte  1: 17 bytes for 'Pixtream Protocol' string.
     - Byte 18: 8 bytes for protocol extensions.
     - Byte 26: 20 bytes for Peer ID.
    """

    message_type = 'H'
    message_struct = struct.Struct('!1s17s8s20s')

    def __init__(self, peer_id):
        """
        Creates the object from a peer_id.

        :param peer_id: ID of the peer sending the message.
        """

        assert isinstance(peer_id, str)
        assert len(peer_id) == 20

        self.peer_id = peer_id

    def encode(self):
        """Encodes the handshake message."""

        return self.message_struct.pack(self.message_type,
                                        'Pixtream Protocol',
                                        '00000000',
                                        self.peer_id)

    @classmethod
    def decode(cls, bytes):
        """Decodes the handshake message."""

        type_, protocol, ext, peer_id = cls.message_struct.unpack(bytes)
        obj = cls(peer_id)
        obj._protocol = protocol
        obj._ext = ext
        obj._type = type_

        return obj

    def validate(self):
        """Checks that the protocol string and messsage types are correct."""

        try:
            return (self._protocol == 'Pixtream Protocol' and
                    self._type == 'H')
        except AttributeError:
            return False


@Message.register
class DataPackageMessage(Message):
    """
    missing
    """

    message_type = 'D'
    message_struct = struct.Struct('!1sI')

    def __init__(self, sequence, data):
        self.sequence = sequence
        self.data = data

    def encode(self):
        """Encodes the handshake message."""

        header = self.message_struct.pack(self.message_type, self.sequence)
        return header + self.data

    @classmethod
    def decode(cls, bytes):
        """Decodes the handshake message."""

        bytes = bytes[:cls.message_struct.size]
        data = bytes[cls.message_struct.size:]

        type_, sequence = cls.message_struct.unpack(bytes)
        message = cls(sequence, data)
        message._type = type_

        return message

    def validate(self):
        """Checks that the protocol string and messsage types are correct."""

        try:
            return (self._type == 'D' and self.sequence > 0)
        except AttributeError:
            return False
