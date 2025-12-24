# coding=utf-8
class Card:
    suits = ['C', 'D', 'H', 'S']

    short_ranks = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    full_ranks = ['2', '3', '4', '5'] + short_ranks  # total 13 ranks

    # This will be used in card logic
    ranks = short_ranks

    # Will be overridden when deck is created
    rank_values = {rank: i for i, rank in enumerate(ranks)}

    # Points mappings can stay the same — only valid in games that use those values
    points21_map = {
        '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 2, 'Q': 3, 'K': 4, 'A': 11
    }

    points_kozel_map = {
        '2': 0, '3': 0, '4': 0, '5': 0, '6': 0,
        '7': 0, '8': 0, '9': 0, '10': 10,
        'J': 2, 'Q': 3, 'K': 4, 'A': 11
    }

    WITCH_RANK = 'K'
    WITCH_SUIT = 'S'

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return "{}{}".format(self.rank, self.suit)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return isinstance(other, Card) and self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))

    def is_good_card(self, trump_suit):
        return self.suit == trump_suit or Card.rank_values[self.rank] >= Card.rank_values['9']

    @classmethod
    def compare_ranks(cls, rank1, rank2):
        return cls.rank_values[rank1] > cls.rank_values[rank2]

    @classmethod
    def beats(cls, defender, attacker, trump):
        if defender.suit == attacker.suit:
            return cls.rank_values[defender.rank] > cls.rank_values[attacker.rank]
        elif defender.suit == trump and attacker.suit != trump:
            return True
        else:
            return False

    def is_witch(self):
        return self.rank == Card.WITCH_RANK and self.suit == Card.WITCH_SUIT

    @classmethod
    def is_witch_card(cls, card):
        """Class helper for arbitrary card objects."""
        return isinstance(card, Card) and card.rank == cls.WITCH_RANK and card.suit == cls.WITCH_SUIT

    @classmethod
    def beats_kozel(cls, defender, attacker, trump):
        """Kozel-specific beating rules."""
        if defender.suit == attacker.suit:
            if attacker.rank == '10':
                return defender.rank == 'A'
            elif defender.rank == '10':
                return attacker.rank != 'A'
        return cls.beats(defender, attacker, trump)

    @classmethod
    def set_deck_type(cls, use_full_deck=False):
        """Set deck to full (52) or short (36) mode and update rank values."""
        cls.ranks = cls.full_ranks if use_full_deck else cls.short_ranks
        cls.rank_values = {rank: i for i, rank in enumerate(cls.ranks)}