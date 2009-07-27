import unittest
import string
import random

from pixtream.peer.splitter import Splitter
from pixtream.peer.joiner import Joiner

class SplitterJoinerTest(unittest.TestCase):

    def test_splitter_joiner_(self):
        SIZE = 4 * (10**3)
        CHUNK_SIZE = SIZE / 100

        self.initial_data = ''.join(random.choice(string.letters)
                                    for _ in range(SIZE))

        splitter = Splitter(CHUNK_SIZE)
        joiner = Joiner()

        packets = []
        self.buffer = bytes()

        def on_data_joined(sender):
            self.buffer += joiner.pop_stream()

        def on_end_join(sender):
            self.assertEqual(self.buffer, self.initial_data)

        def on_new_packet(sender):
            packets.append(sender.pop_packet())

        def on_stream_end(sender):
            random.shuffle(packets)
            for packet in packets:
                joiner.push_packet(packet)
            joiner.end_join()

        splitter.on_new_packet.add_handler(on_new_packet)
        splitter.on_stream_end.add_handler(on_stream_end)
        joiner.on_data_joined.add_handler(on_data_joined)
        joiner.on_end_join.add_handler(on_end_join)

        for char in self.initial_data:
            splitter.push_stream(char)
        splitter.end_stream()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
