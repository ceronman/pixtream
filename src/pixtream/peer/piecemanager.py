"""
Piece manager
"""

import logging
import itertools

__all__ = ['PieceManager']

class PieceManager(object):

    # FIXME: use configuration system
    MAX_REQUESTS = 3

    def __init__(self):
        self.last_continuous_piece = 0
        self.own_pieces = {}
        self.pieces_by_partner = {}
        self.partners_by_piece = {}
        self.pieces_requested_to = {}
        self.pieces_requested_from = {}

    @property
    def own_sequences(self):
        return set(self.own_pieces.keys())

    @property
    def partners_sequences(self):
        return set(self.partners_by_piece.keys())

    def add_new_piece(self, sequence, data):
        self.own_pieces[sequence] = data
        self._update_last()
        logging.info('Last piece: {0}'.format(self.last_continuous_piece))

    def have_piece(self, sequence):
        return sequence in self.own_pieces

    def partner_got_piece(self, partner_id, sequence):
        pieces = self.pieces_by_partner.setdefault(partner_id, set())
        pieces.add(sequence)

        partners = self.partners_by_piece.setdefault(sequence, set())
        partners.add(partner_id)

    def partner_got_pieces(self, partner_id, pieces):
        for piece in pieces:
            self.partner_got_piece(partner_id, piece)

    def get_piece_data(self, sequence):
        return self.own_pieces.get(sequence, None)

    def mark_piece_as_sent(self, partner_id, sequence):
        self.pieces_requested_from[partner_id].remove(sequence)

    def partner_requested_piece(self, partner_id, sequence):
        pieces = self.pieces_requested_from.setdefault(partner_id, set())
        pieces.add(sequence)

    def get_pieces_to_send(self):
        return [(partner_id, sequence)
                for partner_id in self.pieces_requested_from
                for sequence in self.pieces_requested_from[partner_id]
                if self.have_piece(sequence)]

    def mark_piece_as_requested(self, partner_id, sequence):
        pieces = self.pieces_requested_to.setdefault(partner_id, set())
        pieces.add(sequence)

    def can_request_piece(self, partner_id, sequence):
        pieces = self.pieces_requested_to.setdefault(partner_id, set())
        return sequence not in pieces

    def get_pieces_to_request(self):
        """ Implementation of the Rarest First Algorithm """
        missing_pieces = list(self.partners_sequences - self.own_sequences)
        missing_pieces.sort(key=lambda p: len(self.partners_by_piece[p]))

        return missing_pieces[:self.MAX_REQUESTS]

    def best_partner_for_piece(self, piece):
        partners = self.partners_by_piece.get(piece, [])

        if len(partners) == 0:
            return None

        else:
            return next(iter(partners))

    def _update_last(self):
        for piece in itertools.count(self.last_continuous_piece):
            if piece in self.own_pieces:
                self.last_continuous_piece = piece
            else:
                break
