"""
trackermanager.py

Handles connection to the tracker and encoding decoding tracker messages.
"""

import urlparse
import urllib
import json
import logging

from twisted.web import client
from twisted.internet import reactor

from pixtream.util.twistedrepeater import TwistedRepeater

class TrackerManagerError(Exception):
    """
    Errors produced by the TrackerManager.
    """
    pass

class TrackerManager(object):
    """
    Manages the interaction between the Pixtream tracker and
    the Pixtream peer.
    """

    def __init__(self, peer_service, tracker_url):
        """
        Initializes the manager, gets a PeerService object and a URL of the
        tracker.
        """

        self._connect_repeater = TwistedRepeater(self.connect_to_tracker)
        self._first_contact = False

        self.peer_service = peer_service
        self.tracker_url = tracker_url
        self.peer_list = []

    def connect_to_tracker(self):
        """Starts connection with the tracker."""

        deferred = client.getPage(self._request_url)
        deferred.addCallback(self._on_tracker_contact)
        deferred.addErrback(self._on_tracker_contact_error)

    @property
    def _request_url(self):
        """Creates a request URL for the tracker with the GET query."""

        query = dict(peer_id = self.peer_service.peer_id,
                     port = self.peer_service.port)

        if self.peer_service.ip is not None:
            query.update(ip = self.peer_service.ip)

        parts = list(urlparse.urlsplit(self.tracker_url))
        parts[3] = urllib.urlencode(query) # assigns the query part of the URL.

        return urlparse.urlunsplit(parts)

    def _on_tracker_contact(self, content):
        try:
            logging.debug('Recieved tracker response')
            response = json.loads(content)

            if u'failure_reason' in response:
                self._on_tracker_failure(response[u'failure_reason'])
                return

            if u'request_interval' in response:
                self._connect_repeater.seconds = response[u'request_interval']

            if u'peers' in response:
                self.peer_list = response[u'peers']

            if not self._first_contact:
                self._connect_repeater.start_later()

        except Exception as e:
            self._on_tracker_failure(str(e))

    def _on_tracker_contact_error(self, error):
        logging.error('Unable to contact the tracker: ' + str(error.value))
        if not self._first_contact:
            reactor.stop()

    def _on_tracker_failure(self, error):
        logging.error('Tracker failure: ' + error)


