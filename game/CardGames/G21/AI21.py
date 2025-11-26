# coding=utf-8
from CardGames.Classes.Card import Card
from CardGames.Classes.Player import Player

class AI21(Player):
    def __init__(self, name):
        super(AI21, self).__init__(name)

    _THRESHOLDS = {
        'weak':   0.50,
        'medium': 0.40,
        'strong': 0.28,
    }

    def _opponent_category(self, opponent_total):
        """Classify opponent hand strength based on total."""
        if opponent_total is None:
            return 'medium'
        if opponent_total > 21 or opponent_total <= 13:
            return 'weak'
        if 14 <= opponent_total <= 17:
            return 'medium'
        return 'strong'

    def _build_remaining_counts(self, seen_cards):
        """Track remaining cards in the deck after removing seen ones."""
        counts = {r: 4 for r in Card.ranks}
        for card in seen_cards or []:
            if card and card.rank in counts and counts[card.rank] > 0:
                counts[card.rank] -= 1
        return counts

    def _safe_and_improving_stats(self, current_total, counts):
        """
        Count:
        - safe draws (won't bust)
        - improving draws (bring total to 18–21)
        """
        safe, improve, total = 0, 0, 0

        for r in Card.ranks:
            count = counts.get(r, 0)
            if count <= 0:
                continue

            pts = Card.points21_map[r]
            new_total = current_total + pts
            total += count

            if new_total <= 21:
                safe += count
                if 18 <= new_total <= 21:
                    improve += count

        return safe, total, improve

    def _adjust_threshold(self, base, total, opponent_total):
        """Tweak base threshold based on current and opponent hands."""
        th = base

        # Adjust for AI's own hand shape
        if total in (10, 11):
            th -= 0.05
        elif total == 14:
            th += 0.02
        elif total == 15:
            th += 0.05
        elif total == 16:
            th += 0.10

        # Adjust for opponent hand
        if opponent_total is not None:
            if opponent_total > 21:
                th += 0.08
            elif opponent_total >= 18:
                th -= 0.08
            elif opponent_total <= 13:
                th += 0.05

        return min(max(th, 0.0), 0.95)

    def decide(self, seen_cards=None, opponent_total=None):
        """
        Decide whether to 'h' (hit) or 'p' (pass) based on hand and probabilities.
        """
        total = self.total21()

        # Forced decisions
        if total >= 21:
            return 'p'
        if total <= 9:
            return 'h'
        if total >= 17:
            return 'p'

        seen_cards = seen_cards or list(self.hand)
        counts = self._build_remaining_counts(seen_cards)
        safe_cnt, total_cnt, improve_cnt = self._safe_and_improving_stats(total, counts)

        safe_prob = float(safe_cnt) / total_cnt if total_cnt else 0.0
        improve_prob = float(improve_cnt) / total_cnt if total_cnt else 0.0

        # Threshold based on opponent strength
        opp_cat = self._opponent_category(opponent_total)
        base_threshold = self._THRESHOLDS[opp_cat]
        threshold = self._adjust_threshold(base_threshold, total, opponent_total)

        # Fine-tune based on how many cards improve our hand
        if improve_prob < 0.12:
            threshold += 0.02
        elif improve_prob > 0.30:
            threshold -= 0.02

        return 'h' if safe_prob >= threshold else 'p'
