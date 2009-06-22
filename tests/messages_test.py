import unittest
import pixtream.peer.messages as messages
import random
import string

class HandShakeMessageTest(unittest.TestCase):
    def test_iomessage(self):
        peer_id = ''.join(random.choice(string.letters) for i in range(20))

        output = messages.handshake_encode(peer_id)
        input = messages.handshake_decode(output)

        self.assertEqual(peer_id, input[-1])

if __name__ == '__main__':
    unittest.main()

