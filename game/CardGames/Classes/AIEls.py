# coding=utf-8
import random
from Player import Player
from Card import Card

class AIEls(Player):
    def __init__(self, name):
        super(AIEls, self).__init__(name)

    def _get_needed_ranks(self):
        """
        Returns a set of ranks that would improve AI's hand.
        Simple version: return ranks we already have (to make pairs).
        """
        rank_counts = {}
        for card in self.hand:
            rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1
        return set([r for r, count in rank_counts.items() if count >= 1])

    def _decide_best_card_to_sacrifice(self):
        """
        Utility: Return index of lowest-value card not part of a pair.
        """
        rank_counts = {}
        for card in self.hand:
            rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1

        singleton_indices = [
            (i, card) for i, card in enumerate(self.hand)
            if rank_counts[card.rank] == 1
        ]
        if singleton_indices:
            singleton_indices.sort(key=lambda x: Card.rank_values[x[1].rank])
            return singleton_indices[0][0]
        # No singleton, just pick weakest
        sorted_by_rank = sorted(enumerate(self.hand), key=lambda x: Card.rank_values[x[1].rank])
        return sorted_by_rank[0][0]

    def choose_attack_index(self, opponent_hand):
        """
        Choose a card index from opponent's hand to take.
        Heuristic:
            - Try to guess high-value cards by suit/rank
            - Prioritize unseen ranks or suits the AI needs
            - Fallback: random
        """
        needed_ranks = self._get_needed_ranks()
        for i, card in enumerate(opponent_hand):
            if card.rank in needed_ranks:
                return i
        return random.randint(0, len(opponent_hand) - 1)

    def choose_defense_swap(self, selected_card_index):
        """
        Decide whether to swap the card attacker picked (index) with another.
        Returns:
            - index of card to swap with
            - or None to surrender the selected card
        Strategy:
            - Protect cards forming pairs/triples
            - Try to swap with a weak singleton
            - If not available, use decide_best_card_to_sacrifice
        """
        selected_card = self.hand[selected_card_index]
        rank_counts = {}
        for card in self.hand:
            rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1

        # If selected card is part of a pair or triple — try to protect it
        if rank_counts[selected_card.rank] > 1:
            # Find lowest-value singleton to sacrifice
            options = [
                (i, card) for i, card in enumerate(self.hand)
                if rank_counts[card.rank] == 1 and i != selected_card_index
            ]
            if options:
                options.sort(key=lambda x: Card.rank_values[x[1].rank])
                return options[0][0]  # swap with weakest singleton

            # No singleton available, fallback to general sacrificial logic
            fallback = self._decide_best_card_to_sacrifice()
            if fallback != selected_card_index:
                return fallback

        return None  # Accept the loss of selected card