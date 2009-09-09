"""
Piece manager
"""

import logging
import itertools

class PieceManager(object):
    def __init__(self):
        self.last_continuous_piece = 0
        self.own_pieces = {}
        self.pieces_by_partner = {}
        self.partner_by_piece = {}
        self.pieces_sent = {}
        self.pieces_requested = {}

    @property
    def piece_sequences(self):
        return set(self.own_pieces.keys())

    def got_new_piece(self, sequence, data):
        self.own_pieces[sequence] = data
        self._update_last()
        logging.info('Last piece: {0}'.format(self.last_continuous_piece))

    def partner_got_piece(self, partner, sequence):
        pieces = self.pieces_by_partner.setdefault(partner, set())
        pieces.add(sequence)

        partners = self.partner_by_piece.setdefault(sequence, set())
        partners.add(partner)

    def get_piece_data(self, sequence):
        return self.own_pieces.get(sequence, None)

    def piece_sent(self, partner_id, sequence):
        pieces = self.pieces_sent.setdefault(partner_id, set())
        pieces.add(sequence)

    def piece_requested(self, partner_id, sequence):
        pieces = self.pieces_requested.setdefault(partner_id, set())
        pieces.add(sequence)

    def piece_sent_allowed(self, partner_id, sequence):
        pieces = self.pieces_sent.setdefault(partner_id, set())
        return sequence not in pieces

    def piece_request_allowed(self, partner_id, sequence):
        pieces = self.pieces_requested.setdefault(partner_id, set())
        return sequence not in pieces

    def partner_got_pieces(self, partner, pieces):
        for piece in pieces:
            self.partner_got_piece(partner, piece)

    def most_wanted_pieces(self, num):
        pieces = []
        for piece in itertools.count(self.last_continuous_piece):
            if piece not in self.own_pieces:
                pieces.append(piece)
            if len(pieces) == num:
                break

        return pieces

    def best_partner_for_piece(self, piece):
        partners = self.partner_by_piece.get(piece, [])

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
