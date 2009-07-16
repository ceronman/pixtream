import sys
sys.path.append('..')

import unittest
import random
import logging
from twisted.internet import reactor

from pixtream.peer.splitter import Splitter
from pixtream.peer.joiner import Joiner
from pixtream.peer.streamclient import TCPStreamClient

class Test(unittest.TestCase):

    def testTCPStreamClient(self):
        format = '%(asctime)s:%(levelname)s:%(module)s:%(lineno)d: %(message)s'
        logging.basicConfig(level = logging.DEBUG,
                        format = format,
                        stream = sys.stdout)
        splitter = Splitter(10000)
        joiner = Joiner()
        client = TCPStreamClient(splitter)

        packets = []

        self.buffer = bytes()

        def on_data_joined(sender):
            self.buffer += joiner.get_stream()
            print 'got stream'

        def on_end_join(sender):
            file_ = open('result', 'wb')
            file_.write(self.buffer)
            file_.close()
            print 'end join'

        def on_new_packet(sender):
            packets.append(sender.pop_packet())

        def on_stream_end(sender):
            print len(packets)
            random.shuffle(packets)
            for packet in packets:
                print 'pushing:', packet.sequence
                joiner.push_packet(packet)
            joiner.end_join()

        splitter.on_new_packet.add_handler(on_new_packet)
        splitter.on_stream_end.add_handler(on_stream_end)
        joiner.on_data_joined.add_handler(on_data_joined)
        joiner.on_end_join.add_handler(on_end_join)

        client.connect('localhost', 3000)
        reactor.run()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
