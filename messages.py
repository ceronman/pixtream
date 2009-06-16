import struct

class PrefixedStruct(struct.Struct):
    prefix_struct = struct.Struct('!i')
    def prefix_pack(self, *args):
        return self.prefix_struct.pack(self.size) + self.pack(*args)

class HandShakeMessage(object):
    """ Pixtream Protocol handshake message:

        4 bytes: Message Lenght
        17 bytes: "Pixtream Protocol" string
        4 bytes: For future use, leave them blank
        20 bytes: Peer ID
    """

    message_struct = PrefixedStruct('!17s4s20s')
    protocol_string = 'Pixtream Protocol'

    def __init__(self, peer_id):
        self.peer_id = peer_id

    def encode(self):
        return self.message_struct.prefix_pack(self.protocol_string,
                                               '    ',
                                               self.peer_id)

    def decode(self, data):
        try:
            protocol, extra, peer_id = self.message_struct.unpack(data)
            if protocol == self.protocol_string:
                self.peer_id = peer_id
                return True
            return False
        except struct.error:
            return False

