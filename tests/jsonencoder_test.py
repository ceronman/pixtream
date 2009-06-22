import sys
sys.path.append('../..')

import unittest
import json
import time

from pixtream.tracker.jsonencoder import PixtreamJSONEncoder
from pixtream.tracker.peermanager import Peer, PeerManager

class PixtreamJSONEncoderTest(unittest.TestCase):
    def test_encoder(self):
        pm = PeerManager(peer_timeout = 100)
        pm.peers = dict( ('id{0}'.format(i),
                          Peer('id{0}'.format(i),
                               '192.168.1.{0}'.format(i),
                               20000 +  i,
                               time.time()))
                          for i in range(10))

        encoder = PixtreamJSONEncoder()
        output = encoder.encode(pm)

        result = json.loads(output)

        self.assertEqual(result['request_interval'], 100)

        peers = result['peers']
        peers = sorted(peers, key=lambda x: x['id'])

        for i, peer in enumerate(peers):
            self.assertEqual(peer['id'], 'id{0}'.format(i))
            self.assertEqual(peer['ip'], '192.168.1.{0}'.format(i))
            self.assertEqual(peer['port'], 20000 +  i)




if __name__ == '__main__':
    unittest.main()

