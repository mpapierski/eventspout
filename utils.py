from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.defer import Deferred


def getBody(response):
    class BodyReceiver(Protocol):
        def dataReceived(self, data):
            chunks.append(data)
        def connectionLost(self, reason):
            finished.callback(''.join(chunks))

    finished = Deferred()
    chunks = []
    response.deliverBody(BodyReceiver())
    return finished

def waitFor(t):
    d = Deferred()
    def resolve():
        d.callback(None)
    reactor.callLater(t, resolve)
    return d
