import sys
import random

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientCreator

sys.path.append('..')

from pixtream.peer.messages import HandshakeMessage

class Greeter(Protocol):
    def connectionMade(self):
        msg = HandshakeMessage('TE1111' +  ''.join(str(random.randint(0,9))
                                                   for _ in range(14)))
        self.transport.write(msg.prefix_encode())

    def dataReceived(self, data):
        print data

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print 'Error: incorrect arguments'
        sys.exit()

    port = int(sys.argv[1])

    print 'Connecting to port', port

    c = ClientCreator(reactor, Greeter)
    c.connectTCP("localhost", port)
    reactor.run()

