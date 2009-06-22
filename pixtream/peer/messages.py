from pixtream.util.exceptions import handle_exception
import struct

prefix_struct = struct.Struct('!i')
type_struct = struct.Struct('!s')

class MessageDecodingError(Exception):
    pass

def handle_decode_error(exception):
    raise MessageDecodingError('Error decoding')

@handle_exception(struct.error, handle_decode_error)
def get_message_type(self, message):
    return type_struct.unpack(message)

def prefix_message(message):
    size = len(message)
    return prefix_struct.pack(size) + message

# Handshake Message

handshake_struct = struct.Struct('!1s17s8s20s')

def handshake_encode(peer_id):
    return handshake_struct.pack('H', 'Pixtream Protocol', '        ', peer_id)

@handle_exception(struct.error, handle_decode_error)
def handshake_decode(message):
    return handshake_struct.unpack(message)

