"""
Piece manager
"""

class PieceManager(object):
    def __init__(self):
        self.own_pieces = set()
        self.pieces_by_partner = {}

    def got_new_piece(self, piece):
        self.own_pieces.add(piece)

    def partner_got_piece(self, partner, piece):
        partner_pieces = self.pieces_by_partner.setdefault(partner, set())
        partner_pieces.add(piece)

    def partner_got_pieces(self, partner, pieces):
        partner_pieces = self.pieces_by_partner.setdefault(partner, set())
        partner_pieces.update(pieces)
