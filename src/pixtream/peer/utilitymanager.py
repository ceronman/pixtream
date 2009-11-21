"""
Utility Manager. Manages utility factor for every peer
"""

import logging

class UtilityManager(object):

    def __init__(self):
        self.utility_by_peer = {}

    def add_peer_utility(self, peer_id, utility):
        self.utility_by_peer.setdefault(peer_id, 0)
        self.utility_by_peer[peer_id] += utility
        logging.info('Utility Factors {0}'.format(self.utility_by_peer))
