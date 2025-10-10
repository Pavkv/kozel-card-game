# coding=utf-8
import random
from Card import Card
from Player import Player

class AIKozel(Player):
    def __init__(self, name):
        super(AIKozel, self).__init__(name)
        self.seen_cards = set()

    # -------------------------------
    # Memory Management
    # -------------------------------

    def remember_card(self, card):
        """Remember a single revealed card."""
        if isinstance(card, Card):
            self.seen_cards.add(card)

    def remember_cards(self, cards):
        """Remember a list of revealed cards."""
        for c in cards:
            self.remember_card(c)

    def unseen_cards(self, full_deck):
        """Return a list of cards not yet seen (still possibly in play)."""
        return [c for c in full_deck.cards if c not in self.seen_cards]

    # -------------------------------
    # AI Core Logic
    # -------------------------------

    def choose_attack_cards(self, table, trump_suit, opponent_hand_size=None):
        """
        Selects a set of same-suit cards to attack with.
        Never attacks with more cards than opponent can defend (hand size limit).
        """
        self.remember_cards(list(table.keys()) + list(table.values()))

        # Organize hand by suit
        hand_by_suit = {}
        for card in self.hand:
            hand_by_suit.setdefault(card.suit, []).append(card)

        # Collect all candidate same-suit sets
        candidate_sets = []
        for suit, cards in hand_by_suit.items():
            if len(cards) >= 1:
                cards.sort(key=lambda c: (c.suit == trump_suit, Card.rank_values[c.rank]))
                candidate_sets.append(cards)

        if not candidate_sets:
            return []

        # Sort by total point value (prefer low)
        candidate_sets.sort(key=lambda cs: sum(Card.points_kozel_map[c.rank] for c in cs))
        attack_set = candidate_sets[0]

        if opponent_hand_size is not None and len(attack_set) > opponent_hand_size:
            attack_set = attack_set[:opponent_hand_size]

        self.remember_cards(attack_set)
        return attack_set

    def defense(self, attack_card, trump_suit, exclude=None):
        """
        Return one card to defend against `attack_card`, or None to give up.
        `exclude` is a set of already-used cards that cannot be used again this turn.
        """
        self.remember_card(attack_card)

        if exclude is None:
            exclude = set()

        # Filter valid defense candidates
        candidates = [
            c for c in self.hand
            if c not in exclude and Card.beats_kozel(c, attack_card, trump_suit)
        ]

        if not candidates:
            return None

        # Sort: prioritize non-trumps with lowest rank value
        candidates.sort(key=lambda c: (c.suit == trump_suit, Card.rank_values[c.rank]))

        chosen = candidates[0]
        self.remember_card(chosen)
        return chosen

    def discard_if_needed(self, attack_cards):
        """If unable to defend, discard the same number of lowest-value cards."""
        if len(attack_cards) > len(self.hand):
            return []
        self.hand.sort(key=lambda c: Card.points_kozel_map[c.rank])
        discard_cards = self.hand[:len(attack_cards)]
        self.remember_cards(attack_cards + discard_cards)
        return discard_cards
