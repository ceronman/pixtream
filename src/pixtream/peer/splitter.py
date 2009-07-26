'''
Splits streaming data into Pixtream protocol packages
'''

from collections import deque

from pixtream.util.event import Event
from pixtream.peer.specs import DataPacketMessage

class Splitter(object):

    def __init__(self, packet_size):
        self.packet_size = packet_size
        self.on_new_packet = Event()
        self.on_stream_end = Event()

        self._buffer = bytes()
        self._packets = deque()
        self._current_sequence = 0

    def push_stream(self, data):
        self._buffer = self._buffer + data

        if len(self._buffer) >= self.packet_size:
            packet_data = self._buffer[:self.packet_size]
            self._buffer = self._buffer[self.packet_size:]
            self._create_packet(packet_data)

    def end_stream(self):
        self._create_packet(self._buffer)
        self.on_stream_end.call(self)

    def pop_packet(self):
        return self._packets.popleft()

    def _create_packet(self, packet_data):
        packet = DataPacketMessage.create(self._current_sequence, packet_data)
        self._packets.append(packet)
        self._current_sequence += 1
        self.on_new_packet.call(self)
