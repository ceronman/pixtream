'''
Joins Pixtream data packets into a Stream
'''

from itertools import takewhile, count

from pixtream.util.event import Event

class Joiner(object):

    def __init__(self):

        self.on_data_joined = Event()
        self.on_end_join = Event()

        self._buffer = bytes()
        self._current_sequence = 0
        self._packets = {}

    def push_packet(self, packet):
        self._packets[packet.sequence] = packet.data
        self._join_buffer()

    def end_join(self):
        self.on_end_join.call(self)

    def get_stream(self):
        buffer = self._buffer
        self._buffer = bytes()
        return buffer

    def _join_buffer(self):
        sequences = takewhile(lambda seq: seq in self._packets,
                              count(self._current_sequence))

        sequences = list(sequences)

        if len(sequences) > 0:
            self._buffer += ''.join(self._packets[seq] for seq in sequences)

            for sequence in sequences:
                del self._packets[sequence]

            self._current_sequence = sequences[-1] + 1

            self.on_data_joined.call(self)


