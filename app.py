import logging
import urlparse
import json
import itertools
from StringIO import StringIO
from pprint import pformat
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredQueue, setDebugging, inlineCallbacks
from twisted.web.client import Agent, ProxyAgent, FileBodyProducer
from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import UNIXClientEndpoint, TCP4ClientEndpoint
from twisted.web.http_headers import Headers
from twisted.internet.error import ConnectionRefusedError
from config import CALLBACK_URL, DOCKER_HOST
from json_producer import JsonProducer
from events import DockerEventsProtocol
from utils import getBody, waitFor

log = logging.getLogger(__name__)
queued_events = DeferredQueue()
http_agent = Agent(reactor)


def callback(response):
    """GET /events

    Called after received response from Docker.
    """
    log.debug('Callback')
    log.debug('Response version: {}'.format(response.version))
    log.debug('Response code: {}'.format(response.code))
    log.debug('Response phrase: {}'.format(response.phrase))
    log.debug('Response headers: {}'.format(
        pformat(list(response.headers.getAllRawHeaders()))))
    dfd = Deferred()
    protocol = DockerEventsProtocol(queued_events, dfd)
    response.deliverBody(protocol)
    return dfd


def errback(e):
    log.error('Error: {0}'.format(e))


@inlineCallbacks
def consumeEvents():
    for event_number in itertools.count(1):
        log.info('Waiting for event... {}'.format(event_number))
        event = yield queued_events.get()
        log.debug('Event: {!r}'.format(event))
        while True:
            try:
                response = yield http_agent.request(
                    'POST',
                    CALLBACK_URL,
                    Headers({
                        'Content-Type': ['application/javascript']
                    }),
                    FileBodyProducer(StringIO(json.dumps(event))))
                response_body = yield getBody(response)       
                log.debug('Event transmitted')
                log.debug('Transmit response version: {}'.format(response.version))
                log.debug('Transmit response code: {}'.format(response.code))
                log.debug('Transmit response phrase: {}'.format(response.phrase))
                log.debug('Transmit response body: {!r}'.format(response_body))
                if response.code != 200:
                    log.warn('Transmitted response code: {}. Retrying...'.format(response.code))
                    yield waitFor(1.0)
                    continue
                break
            except ConnectionRefusedError as e:
                log.error('{}'.format(e))
                yield waitFor(1.0)
                continue


def main():
    reactor.callLater(0, consumeEvents)
    logging.basicConfig(level=logging.DEBUG)
    log.debug('Starting...')
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


if __name__ == '__main__':
    setDebugging(True)
    reactor.callLater(0, main)
    reactor.run()
