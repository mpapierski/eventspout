import logging
import json
from twisted.internet.protocol import Protocol

log = logging.getLogger(__name__)


class DockerEventsProtocol(Protocol):
    """Protocol that reads docker stream.
    """

    def __init__(self, queue, finished):
        self.queue = queue
        self.finished = finished

    def connectionLost(self, reason):
        self.finished.callback(None)

    def dataReceived(self, data):
        log.debug('Data: {!r}'.format(data))
        event = json.loads(data)
        self.queue.put(event)
