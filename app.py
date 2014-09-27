import logging
import urlparse
from pprint import pformat
from twisted.internet.task import react
from twisted.internet.defer import Deferred
from twisted.web.client import Agent, ProxyAgent
from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import UNIXClientEndpoint, TCP4ClientEndpoint

from config import CALLBACK_URL, DOCKER_HOST

log = logging.getLogger(__name__)

class DockerEventsProtocol(LineReceiver):
    """Protocol that reads docker stream
    """
    def __init__(self, finished):
        self.finished = finished
    def connectionLost(self, reason):
        log.warn('Reason: {}'.format(reason.getErrorMessage()))
        self.finished.callback(None)
    def lineReceived(self, line):
        log.debug('Event: {!r}'.format(line))

def callback(response):
    log.debug('Callback')
    log.debug('Response version: {}'.format(response.version))
    log.debug('Response code: {}'.format(response.code))
    log.debug('Response phrase: {}'.format(response.phrase))
    log.debug('Response heaedrs: {}'.format(pformat(list(response.headers.getAllRawHeaders()))))
    dfd = Deferred()
    protocol = DockerEventsProtocol(dfd)
    response.deliverBody(protocol)
    return dfd

def errback(e):
    log.error('Error: {0}'.format(e))

@react
def main(reactor):
    logging.basicConfig(level=logging.DEBUG)
    log.info('Starting...')
    o = urlparse.urlparse(DOCKER_HOST)
    if o.scheme == 'unix':
        endpoint = UNIXClientEndpoint(reactor, o.path)
    elif o.scheme in ('tcp', 'http'):
        port = o.port or 80
        endpoint = TCP4ClientEndpoint(reactor, o.hostname, port)
    else:
        assert 0
    agent = ProxyAgent(endpoint)
    d = agent.request('GET', '/events')
    d.addCallback(callback)
    d.addErrback(errback)
    return d