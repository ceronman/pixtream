"""
trackermanager.py

Handles connection to the tracker and encoding decoding tracker messages.
"""

import urlparse
import urllib
import json

from twisted.web import client

from twistedrepeater import TwistedRepeater

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
                     ip = self.peer_service.ip,
                     port = self.peer_service.port)

        parts = list(urlparse.urlsplit(self.tracker_url))
        parts[3] = urllib.urlencode(query) # assigns the query part of the URL.

        return urlparse.urlunsplit(parts)

    def _on_tracker_contact(self, content):
        try:
            self.peer_list = json.loads(content)
            self._connect_repeater.seconds = 30 # FIXME: get value from tracker
        except:
            raise TrackerManagerError('Could not parse tracker response')

    def _on_tracker_contact_error(self, error):
        raise TrackerManagerError('Unable to contact the server\n' + error)


