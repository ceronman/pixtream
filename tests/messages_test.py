import sys
sys.path.append('..')
import unittest
import messages

class HandShakeMessageTest(unittest.TestCase):
    def test_encoding_decoding(self):
        peer_id = 'LBzNXCBqIQtzOHDuWLvt'
        input = messages.HandShakeMessage(peer_id)
        encoded_message = input.encode()
        output = messages.HandShakeMessage('')
        result = output.decode(encoded_message[4:])
        self.assert_(result,
                     'Encoding failure: {0}'.format(encoded_message))
        self.assert_(output.peer_id == peer_id,
                     '{0} != {1}'.format(output.peer_id, peer_id))

if __name__ == '__main__':
    unittest.main()

