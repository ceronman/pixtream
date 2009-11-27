"""
Manage communication with a Pixtream Tracker.

Encodes and decodes tracker messages. Sends periodical reports to the tracker.
"""

import urlparse
import urllib
import json
import logging

from twisted.web import client

from pixtream.util.twistedrepeater import TwistedRepeater
from pixtream.util.event import Event
from pixtream.peer.peerdatabase import Peer

__all__ = ['TrackerManager', 'TrackerManagerError', 'TrackerStatus']

class TrackerManagerError(Exception):
    """
    Errors produced by the TrackerManager.
    """
    pass

class TrackerStatus(object):
    OK, STANDBY, ERROR = range(3)

    def __init__(self, status, message):
        self.status = status
        self.message = message

class TrackerManager(object):
    """
    Manages the connection with the tracker
    """

    DEFAULT_ANNOUNCE = 30

    #TODO: Eliminate tracker_url parameter
    def __init__(self, tracker_url, peer):
        """
        Initializes the manager.
        """

        self._announce_repeater = TwistedRepeater(self.announce,
                                                  self.DEFAULT_ANNOUNCE)
        self._utility_repeater = TwistedRepeater(self.report_utility,
                                                 self.DEFAULT_ANNOUNCE)

        self.tracker_url = tracker_url
        self.peer = peer
        self.utility_by_peer = {}

        self.peer_list = []
        self.status = TrackerStatus(TrackerStatus.STANDBY, 'Ready to connect')

        self.on_updated = Event()
        self.on_status_changed = Event()

    def connect_to_tracker(self):
        self._announce_repeater.start_now()
        self._utility_repeater.start_now()

    def announce(self):
        """Starts connection with the tracker."""

        logging.debug('Announcing to tracker')
        deferred = client.getPage(self._create_announce_url())
        deferred.addCallback(self._on_announce_response)
        deferred.addErrback(self._on_tracker_error)

    def report_utility(self):
        if len(self.utility_by_peer) == 0:
            return
        deferred = client.getPage(self._create_utility_url())
        deferred.addCallback(self._on_utility_response)
        deferred.addErrback(self._on_tracker_error)

    def _create_announce_url(self):
        """Creates a request URL for the tracker with the GET query."""

        query = dict(peer_id = self.peer.id,
                     port = self.peer.port)

        if self.peer.ip is not None:
            query.update(ip = self.peer.ip)

        parts = list(urlparse.urlsplit(self.tracker_url))
        parts[2] += '/announce' # path
        parts[3] = urllib.urlencode(query) # query

        return urlparse.urlunsplit(parts)

    def _create_utility_url(self):
        parts = list(urlparse.urlsplit(self.tracker_url))
        parts[2] += '/utility'
        parts[3] = urllib.urlencode(self.utility_by_peer) # query.

        return urlparse.urlunsplit(parts)

    def _on_tracker_error(self, error):
        logging.error('Unable to contact the tracker: ' + str(error.value))
        self._change_status(TrackerStatus.ERROR,
                            'Unable to contact the tracker')

    def _on_announce_response(self, content):
        try:
            logging.debug('Received tracker announce response')
            response = json.loads(content)

            if 'failure_reason' in response:
                self._on_announce_failure(response['failure_reason'])
                return

            if 'request_interval' in response:
                self._announce_repeater.seconds = response['request_interval']

            if 'peers' in response:
                self._update_peers(response['peers'])

            self._change_status(TrackerStatus.OK, 'OK')

        except Exception as e:
            self._on_announce_failure(str(e))

    def _on_announce_failure(self, error):
        logging.error('Tracker announce failure: ' + error)
        self._change_status(TrackerStatus.ERROR, error)

    def _on_utility_response(self, content):
        logging.debug('Received tracker utility response')
        response = json.loads(content)

        if 'failure_reason' in response:
            self._on_utility_failure(response['failure_reason'])
            return

    def _on_utility_failure(self, error):
        logging.error('Tracker utility failure: ' + error)
        self._change_status(TrackerStatus.ERROR, error)

    def _update_peers(self, peer_list):
        try:
            self.peer_list = []
            for peer_dict in peer_list:
                id = peer_dict['id']
                ip = peer_dict['ip']
                port = peer_dict['port']
                uf = peer_dict['utility_factor']
                self.peer_list.append(Peer(id, ip, port, uf))
            self.on_updated.call(self, self.peer_list)
        except Exception as e:
            raise TrackerManagerError('Unable to convert peer list: ' + str(e))

    def _change_status(self, status, message):
        if self.status.status == status and self.status.message == message:
            return
        self.status = TrackerStatus(status, message)
        self.on_status_changed.call(self, self.status)
