"""
Defines base classes for messages of the Pixtream Protocol.
"""

import struct

__all__ = ['Field', 'FixedLengthMessage', 'Message', 'MessageException',
           'Payload', 'VariableLengthMessage']

class Field(object):
    """
    Simple for to define Fields in Message specs
    """

    def __init__(self, struct_string, name, doc):
        self.name = name
        self.struct_string = struct_string
        self.doc = doc

class Payload(object):
    """
    Simple form to define Payload in Message specs
    """

    def __init__(self, doc):
        self.doc = doc

class MessageException(Exception):
    """
    Exception for errors with messages operations
    """

    def __init__(self, message, data=''):
        super(MessageException, self).__init__(message)
        self.received_data = data

class Message(object):
    """
    Base class for messages.

    Can be used to parse new messages and create appropriate objects.
    """

    message_header = '?'
    _header_map = {}
    _prefix_struct = struct.Struct('>I')

    @classmethod
    def register(cls, message_class):
        """
        Registers a class message.

        Decorator used to register the class message_header in a dictionary.
        This way messages could be identified and objects of proper classes
        will be created
        """

        assert issubclass(message_class, Message)
        assert len(message_class.message_header) == 1
        assert message_class.message_header not in cls._header_map
        assert hasattr(message_class, 'fields')

        message_class._parse_fields()
        message_class._create_message_struct()

        cls._header_map[message_class.message_header] = message_class
        return message_class

    @classmethod
    def parse(cls, data):
        """
        Parse a byte string and creates a message object

        Parses a message byte string got from the network and creates a proper
        Message object of the right subclass and _unpack de string in that object
        """

        if len(data) == 0:
            raise MessageException('Decoding empty message')

        message_type = data[0]
        message_class = cls._header_map.get(message_type, None)

        if message_class is None:
            raise MessageException('Got unregistered message', data)

        message = message_class()

        try:
            message._unpack(data)
        except struct.error:
            raise MessageException('Message not well formatted', data)

        return message

    def pack(self):
        """
        Pack the message object into a byte string.

        Packs the message into a byte string to be send trough the network
        """

        if not self.is_valid():
            raise MessageException("Trying to pack an invalid message")
        values = [getattr(self, name) for name in self.field_names]
        return self._message_struct.pack(*values)

    def pack_prefixed(self):
        """
        Pack the message with a prefix

        Works as pack but returns the message with a four bytes integer
        representing the size of the message
        """

        message = self.pack()
        return self._prefix_struct.pack(len(message)) + message

    def is_valid(self):
        """Returns True if the data in the message is valid"""
        try:
            return (self.message_header == self.__class__.message_header and
                    all(self.valid_conditions()))
        except:
            return False

    def valid_conditions(self):
        """
        Generators that yields conditions necessary for the message to be valid

        Subclasses should override this method
        """
        return
        yield

    @classmethod
    def create(cls):
        """
        Create a new packet.

        Use this instead of the default constructor
        to build a new message object.
        Subclasses should override this method
        """
        return cls()

    def _unpack(self, data):
        fields = self._message_struct.unpack(data)
        for i, name in enumerate(self.field_names):
            setattr(self, name, fields[i])

    @classmethod
    def _parse_fields(cls):
        cls.field_names = ['message_header']
        cls.field_structs = ['s'] # struct string for message_header

        for field in cls.fields:
            assert isinstance(field, Field)
            cls.field_names.append(field.name)
            cls.field_structs.append(field.struct_string)

    @classmethod
    def _create_message_struct(cls):
        struct_string = '>' # big endian
        struct_string += ''.join(cls.field_structs)
        cls._message_struct = struct.Struct(struct_string)

class FixedLengthMessage(Message):
    """
    Base class for Messages with fixed length
    """

class VariableLengthMessage(Message):
    """
    Base class for Messages with variable lenght
    """

    def _unpack(self, data):
        payload = data[self._message_struct.size:]
        data = data[:self._message_struct.size]
        super(VariableLengthMessage, self)._unpack(data)
        self.unpack_payload(payload)

    def pack(self):
        """Packs the fixed part of the message plus a payload"""
        return super(VariableLengthMessage, self).pack() + self.pack_payload()

    def unpack_payload(self, payload):
        """
        Unpacks the payload

        Subclasses should override this method
        """

        self.payload = payload

    def pack_payload(self):
        """
        Returns a byte string with the payload packed

        Subclasses should override this method
        """
        return self.payload
