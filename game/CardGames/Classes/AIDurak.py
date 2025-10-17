from Card import Card
from Player import Player

class AIDurak(Player):
    def __init__(self, name):
        super(AIDurak, self).__init__(name)
        self.seen_cards = set()
        self.player_hand_estimate = set()

        self._full_deck = {Card(rank, suit) for suit in Card.suits for rank in Card.ranks}
        self._unseen_cache = None
        self._cache_dirty = True

    def _update_unseen_cache(self):
        """ Update the cache of unseen cards if it is marked dirty."""
        if self._cache_dirty:
            known = self.seen_cards | set(self.hand)
            self._unseen_cache = list(self._full_deck - known)
            self._cache_dirty = False

    def _mark_dirty(self):
        """ Mark the unseen cache as dirty to be updated later."""
        self._cache_dirty = True

    def _remember_card(self, card):
        """ Remember a card that has been played or seen."""
        if card not in self.seen_cards:
            self.seen_cards.add(card)
            self._mark_dirty()
    
    def _unseen_cards(self):
        """ Return a list of cards that have not been seen (played or in hand)."""
        self._update_unseen_cache()
        return self._unseen_cache

    def _estimate_player_has_trumps(self, trump_suit):
        """ Estimate if the opponent might still have trump cards based on unseen cards."""
        return any(c.suit == trump_suit for c in self._unseen_cards())

    def remember_table(self, table):
        """ Remember cards that have been played on the table."""
        for attack_card, (beaten, defend_card) in table.table.items():
            self._remember_card(attack_card)
            if defend_card:
                self._remember_card(defend_card)

    def remember_discard(self, discard_iterable):
        """ Remember cards that have been discarded."""
        for c in discard_iterable:
            self._remember_card(c)

    def choose_throw_ins(self, table, defender_hand_size, trump_suit):
        """ Choose cards to throw in after initial attack, given the current table state and defender's hand size."""
        if defender_hand_size <= 0:
            return []

        table_ranks = table.qualifier_set
        candidates = [c for c in self.hand if c.rank in table_ranks]
        candidates.sort(key=lambda c: (c.suit == trump_suit, Card.rank_values[c.rank]))

        return candidates[:defender_hand_size]

    def choose_attack_cards(self, table, trump_suit, defender_hand_size):
        """ Choose cards to attack with, given the current table state and defender's hand size."""
        if defender_hand_size <= 0:
            return []

        has_trump_left = self._estimate_player_has_trumps(trump_suit)
        table_ranks = table.qualifier_set
        hand_sorted = sorted(self.hand, key=lambda c: (c.suit == trump_suit, Card.rank_values[c.rank]))

        attack_cards = []

        if not table:
            first = next((c for c in hand_sorted if c.suit != trump_suit), hand_sorted[0])
            attack_cards.append(first)
            for c in hand_sorted:
                if len(attack_cards) >= defender_hand_size:
                    break
                if c is not first and c.rank == first.rank:
                    attack_cards.append(c)
        else:
            for c in hand_sorted:
                if len(attack_cards) >= (defender_hand_size + table.num_unbeaten()):
                    break
                if c.rank in table_ranks:
                    if has_trump_left and c.suit != trump_suit:
                        attack_cards.append(c)
                    elif not has_trump_left or c.suit == trump_suit:
                        attack_cards.append(c)

        return attack_cards

    def defense(self, attack_card, trump_suit, exclude=None):
        """ Choose a card to beat the given attack_card, or None if cannot defend."""
        exclude = exclude or set()
        has_trump_left = self._estimate_player_has_trumps(trump_suit)

        candidates = [
            c for c in self.hand
            if c not in exclude and Card.beats(c, attack_card, trump_suit)
        ]

        if not candidates:
            return None

        candidates.sort(key=lambda c: (c.suit == trump_suit, Card.rank_values[c.rank]))

        if has_trump_left:
            for c in candidates:
                if c.suit != trump_suit:
                    return c

        return candidates[0]
