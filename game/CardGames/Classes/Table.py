from collections import OrderedDict
from Card import Card

class Table:
    def __init__(self, qualifier="rank"):
        """
        qualifier can be:
        - "rank": only same ranks allowed (Durak-style)
        - "suit": only same suits allowed (Kozel-style)
        - "both": match by rank or suit (mixed variant)
        """
        self.table = OrderedDict()  # {attack_card: [is_beaten: bool, defending_card: Card or None]}
        self.qualifier = qualifier
        self.qualifier_set = set()

    def __str__(self):
        return "Table: {}".format(", ".join(str(card) for card in self.table))

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.table)

    def keys(self):
        return self.table.keys()

    def values(self):
        return [v[1] for v in self.table.values()]

    # ---------------------- Core logic ---------------------- #

    def _get_qualifier_value(self, card):
        """Returns the card field used to compare (rank/suit)."""
        if self.qualifier == "rank":
            return card.rank
        elif self.qualifier == "suit":
            return card.suit
        elif self.qualifier == "both":
            # both ranks and suits can qualify
            return card.rank, card.suit
        else:
            raise ValueError("Unknown qualifier: {}".format(self.qualifier))

    def can_append(self, card):
        """Check if a card can be placed on table based on qualifier."""
        if not self.table:
            return True
        if self.qualifier == "both":
            # can play if either rank or suit matches any existing card
            ranks = {c.rank for c in self.table}
            suits = {c.suit for c in self.table}
            return card.rank in ranks or card.suit in suits
        else:
            value = self._get_qualifier_value(card)
            return value in self.qualifier_set

    def append(self, card):
        """Add new attacking card to table if allowed."""
        if not self.can_append(card):
            return False
        self.table[card] = [False, None]
        # store qualifier value(s)
        if self.qualifier == "both":
            self.qualifier_set.add(card.rank)
            self.qualifier_set.add(card.suit)
        else:
            self.qualifier_set.add(self._get_qualifier_value(card))
        return True

    def beat(self, attack_card, defend_card):
        """Mark attack card as beaten and record defending card."""
        if attack_card in self.table:
            self.table[attack_card] = [True, defend_card]
            if self.qualifier == "both":
                self.qualifier_set.add(defend_card.rank)
                self.qualifier_set.add(defend_card.suit)
            else:
                self.qualifier_set.add(self._get_qualifier_value(defend_card))

    def can_beat(self, defender_hand, trump_suit):
        """Check if defender can beat all unbeaten cards."""
        for attack_card, (is_beaten, _) in self.table.items():
            if is_beaten:
                continue
            if self.qualifier == "suit":
                if not any(Card.beats_kozel(def_card, attack_card, trump_suit) for def_card in defender_hand):
                    return False
            else:
                if not any(Card.beats(def_card, attack_card, trump_suit) for def_card in defender_hand):
                    return False
        return True

    def can_transfer(self):
        """Check if a card can be used to transfer the attack."""
        if not self.table or len(self.qualifier_set) != 1:
            return False
        return True

    # ---------------------- Utility methods ---------------------- #

    def num_beaten(self):
        return sum(1 for beaten, _ in self.table.values() if beaten)

    def num_unbeaten(self):
        return sum(1 for beaten, _ in self.table.values() if not beaten)

    def first_unbeaten(self):
        for i, (attack_card, (is_beaten, _)) in enumerate(self.table.items()):
            if not is_beaten:
                return i, attack_card
        return None, None

    def beaten(self):
        return all(status[0] for status in self.table.values()) if self.table else False

    def clear(self):
        self.table.clear()
        self.qualifier_set.clear()