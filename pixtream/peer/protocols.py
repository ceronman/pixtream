from twisted.protocols.basic import Int32StringReceiver

class PixtreamProtocol(Int32StringReceiver):
    def send_hanshake(self):
        pass
