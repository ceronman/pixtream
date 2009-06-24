import struct

class MessageDecodingError(Exception):
    pass

class Message(object):

    _type_map = {}
    _prefix_struct = struct.Struct('!i')
    _type_struct = struct.Struct('!s')

    message_type = '?'
    message_struct = struct.Struct('!i')

    @classmethod
    def register(cls, class_):
        cls._type_map[class_.message_type] = class_
        return class_

    @classmethod
    def decode(cls, bytes):
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
        return self.message_struct.pack(self.message_type)

    def prefix_encode(self):
        message = self.encode()
        return Message._prefix_struct.pack(len(message)) + message

    def validate(self):
        return True

@Message.register
class HandshakeMessage(Message):

    message_type = 'H'

    message_struct = struct.Struct('!1s17s8s20s')

    def __init__(self, peer_id):
        self.peer_id = peer_id

    def encode(self):
        return self.message_struct.pack(self.message_type,
                                        'Pixtream Protocol',
                                        '0000',
                                        self.peer_id)

    @classmethod
    def decode(cls, bytes):
        type_, protocol, ext, peer_id = cls.message_struct.unpack(bytes)
        obj = cls(peer_id)
        obj._protocol = protocol
        obj._ext = ext
        obj._type = type_

        return obj

    def validate(self):
        try:
            return (self._protocol == 'Pixtream Protocol' and
                    self._type == 'H')
        except AttributeError:
            return False
