import unittest
import random
import string

import pixtream.peer.messages as msg

class HandShakeMessageTest(unittest.TestCase):
    def test_iomessage(self):
        peer_id = ''.join(random.choice(string.letters) for _ in range(20))

        handshake = msg.HandshakeMessage(peer_id)

        bytes = handshake.encode()
        new_handshake = msg.Message.decode(bytes)

        self.assert_(new_handshake.validate())
        self.assertEqual(new_handshake.peer_id, peer_id)

    def test_prefix(self):
        peer_id = ''.join(random.choice(string.letters) for _ in range(20))

        handshake = msg.HandshakeMessage(peer_id)

        bytes = handshake.encode()
        prefixed_bytes = handshake.prefix_encode()

        self.assertEqual(prefixed_bytes[:4], '\x00\x00\x00.')

    def test_identity(self):
        peer_id = ''.join(random.choice(string.letters) for _ in range(20))

        handshake = msg.HandshakeMessage(peer_id)

        bytes = handshake.encode()
        new_handshake = msg.Message.decode(bytes)

        self.assert_(isinstance(new_handshake, msg.HandshakeMessage))


if __name__ == '__main__':
    unittest.main()

