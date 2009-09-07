"""
Piece manager
"""

import logging
import itertools

class PieceManager(object):
    def __init__(self):
        self.last_continuous_piece = 0
        self.own_pieces = set()
        self.pieces_by_partner = {}
        self.partner_by_piece = {}

    def got_new_piece(self, piece):
        self.own_pieces.add(piece)
        self._update_last()
        logging.info('Last piece: {0}'.format(self.last_continuous_piece))

    def partner_got_piece(self, partner, piece):
        pieces = self.pieces_by_partner.setdefault(partner, set())
        pieces.add(piece)

        partners = self.partner_by_piece.setdefault(piece, set())
        partners.add(partner)

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
