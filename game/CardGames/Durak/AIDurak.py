# coding=utf-8
from CardGames.Classes.Card import Card
from CardGames.Classes.Player import Player

class AIDurak(Player):
    def __init__(self, name):
        Player.__init__(self, name)
        self.seen_cards = set()

        self._full_deck = set()
        for suit in Card.suits:
            for rank in Card.ranks:
                self._full_deck.add(Card(rank, suit))

        self._unseen_cache = None
        self._cache_dirty = True

    # -------------------------
    # Cache helpers
    # -------------------------

    def _update_unseen_cache(self):
        """Update unseen cards cache if dirty."""
        if self._cache_dirty:
            known = self.seen_cards | set(self.hand)
            self._unseen_cache = list(self._full_deck - known)
            self._cache_dirty = False

    def _mark_dirty(self):
        """Mark caches as dirty."""
        self._cache_dirty = True

    def _remember_card(self, card):
        """Remember a seen card."""
        if card not in self.seen_cards:
            self.seen_cards.add(card)
            self._mark_dirty()

    def _unseen_cards(self):
        """Get the list of unseen cards."""
        self._update_unseen_cache()
        return self._unseen_cache

    def _estimate_player_has_trumps(self, trump_suit):
        """Estimate if a player has trumps based on unseen cards."""
        unseen = self._unseen_cards()
        return len([c for c in unseen if c.suit == trump_suit]) > 0

    # -------------------------
    # Memory
    # -------------------------

    def remember_table(self, table):
        """AI remembers cards on the table."""
        for attack_card, (beaten, defend_card) in table.table.items():
            self._remember_card(attack_card)
            if defend_card:
                self._remember_card(defend_card)

    def remember_discard(self, discard_iterable):
        """AI remembers discarded cards."""
        for c in discard_iterable:
            self._remember_card(c)

    # -------------------------
    # AI Decisions
    # -------------------------

    def choose_throw_ins(self, table, defender, trump_suit):
        """AI chooses throw-ins."""

        # AI must NOT throw-in to itself
        if self == defender:
            return []

        # Cannot throw if defender will pick up everything
        if len(defender.hand) == 0:
            return []

        ranks = table.qualifier_set
        candidates = [c for c in self.hand if c.rank in ranks]

        # Sort by weakest first
        candidates.sort(key=lambda c: (c.suit == trump_suit, Card.rank_values[c.rank]))

        return candidates

    def choose_attack_cards(self, table, trump_suit, defender_hand_size, full_throw):
        """AI chooses attack cards."""
        if defender_hand_size <= 0:
            return []

        has_trump_left = self._estimate_player_has_trumps(trump_suit)
        table_ranks = table.qualifier_set
        hand_sorted = sorted(self.hand, key=lambda c: (c.suit == trump_suit, Card.rank_values[c.rank]))

        # First attack of round
        if not table:
            first = None
            for c in hand_sorted:
                if c.suit != trump_suit:
                    first = c
                    break
            if first is None:
                first = hand_sorted[0]

            attack_cards = [first]

            # add matching ranks
            for c in hand_sorted:
                if len(attack_cards) >= defender_hand_size:
                    break
                if c is not first and c.rank == first.rank:
                    attack_cards.append(c)

            return attack_cards

        # Additional attacks
        attack_cards = []
        limit = defender_hand_size - table.num_unbeaten()

        for c in hand_sorted:
            if len(attack_cards) >= limit or (not full_throw and len(table) + len(attack_cards) >= 6):
                break
            if c.rank in table_ranks:
                if has_trump_left and c.suit != trump_suit:
                    attack_cards.append(c)
                elif not has_trump_left or c.suit == trump_suit:
                    attack_cards.append(c)

        return attack_cards

    def defense(self, attack_card, trump_suit, exclude=None):
        """AI chooses a defense card."""
        exclude = exclude or set()
        has_trump_left = self._estimate_player_has_trumps(trump_suit)

        candidates = [c for c in self.hand if c not in exclude and Card.beats(c, attack_card, trump_suit)]
        if not candidates:
            return None

        candidates.sort(key=lambda c: (c.suit == trump_suit, Card.rank_values[c.rank]))

        if has_trump_left:
            for c in candidates:
                if c.suit != trump_suit:
                    return c

        return candidates[0]

    def should_transfer(self, table, trump_suit):
        """
        Determine if the AI should transfer the attack instead of defending.

        Returns: (bool, Card) — whether to transfer and which card to use
        """

        # Get the rank of the first attacking card
        first_rank = table.keys()[0].rank

        if not first_rank:
            return False, None

        # Find all cards in hand with same rank
        candidates = [c for c in self.hand if c.rank == first_rank]

        if not candidates:
            return False, None

        unseen = self._unseen_cards()
        unseen_same_rank = len([c for c in unseen if c.rank == first_rank])

        # Heuristic: if almost all cards of this rank are visible (seen or in hand), it's safe
        known_same_rank = len([c for c in self.seen_cards if c.rank == first_rank]) + len(candidates)
        safe_to_transfer = known_same_rank - unseen_same_rank >= 3

        # if not safe_to_transfer:
        #     return False, None

        # Prefer weakest card to transfer with
        candidates.sort(key=lambda c: (c.suit == trump_suit, Card.rank_values[c.rank]))

        return True, candidates[0]