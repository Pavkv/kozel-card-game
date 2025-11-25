# coding=utf-8

from CardGames.Classes.CardGame import CardGame
from CardGames.Classes.Card import Card
from CardGames.Classes.AIEls import AIEls

class ElsGame(CardGame):
    def __init__(self, player_name, opponent_name, biased_draw, us_rules=False):
        CardGame.__init__(self, player_name, biased_draw)
        self.opponent = AIEls(opponent_name)
        self.round = 1
        self.turn = 1
        self.us_rules = us_rules

    # ---------- internals ----------
    def _evaluate_hand(self, cards):
        ranks = [card.rank for card in cards]
        suits = [card.suit for card in cards]
        rank_order = Card.rank_values

        rank_counts = {}
        suit_counts = {}
        for r in ranks:
            rank_counts[r] = rank_counts.get(r, 0) + 1
        for s in suits:
            suit_counts[s] = suit_counts.get(s, 0) + 1

        rank_values = sorted([rank_order[r] for r in ranks], reverse=True)

        def is_straight(values):
            values = sorted(set(values), reverse=True)
            for i in range(len(values) - 4):
                window = values[i:i + 5]
                if window == list(range(window[0], window[0] - 5, -1)):
                    return True, window
            return False, []

        flush_suit = next((suit for suit in suit_counts if suit_counts[suit] >= 5), None)

        flush_cards = []
        if flush_suit:
            flush_cards = sorted(
                [card for card in cards if card.suit == flush_suit],
                key=lambda c: rank_order[c.rank],
                reverse=True
            )

        is_straight_all, straight_vals = is_straight(rank_values)
        is_straight_flush, straight_flush_vals = False, []
        if flush_suit:
            flush_values = [rank_order[c.rank] for c in flush_cards]
            is_straight_flush, straight_flush_vals = is_straight(flush_values)

        # Frequency map
        freq_map = {}
        for rank in rank_counts:
            count = rank_counts[rank]
            val = rank_order[rank]
            if count not in freq_map:
                freq_map[count] = []
            freq_map[count].append(val)

        for freq in freq_map:
            freq_map[freq].sort(reverse=True)

        # Helper: create result and return original indexes of the selected cards
        def hand(name, rank, tiebreakers, combo_cards):
            indices = []
            used = set()
            for card in combo_cards:
                for i, c in enumerate(cards):
                    if c == card and i not in used:
                        indices.append(i)
                        used.add(i)
                        break
            return name, rank, tiebreakers, indices

        # Helper: pick only exact number of cards for each rank
        def select_cards_for_values(values_needed, count_map):
            selected = []
            used = set()
            for val in values_needed:
                needed = count_map[val]
                found = 0
                for i, c in enumerate(cards):
                    if rank_order[c.rank] == val and i not in used:
                        selected.append(c)
                        used.add(i)
                        found += 1
                        if found == needed:
                            break
            return selected

        # Combinations
        if is_straight_flush and max(straight_flush_vals) == rank_order['A']:
            combo_cards = []
            for v in straight_flush_vals:
                for c in flush_cards:
                    if rank_order[c.rank] == v and c not in combo_cards:
                        combo_cards.append(c)
                        break
            return hand("Флеш-Рояль", 10, [rank_order['A']], combo_cards)

        elif is_straight_flush:
            combo_cards = []
            for v in straight_flush_vals:
                for c in flush_cards:
                    if rank_order[c.rank] == v and c not in combo_cards:
                        combo_cards.append(c)
                        break
            return hand("Стрит-флеш", 9, straight_flush_vals, combo_cards)

        elif 4 in freq_map:
            four = freq_map[4][0]
            combo_cards = select_cards_for_values([four], {four: 4})
            return hand("Каре", 8, [four], combo_cards)

        elif 3 in freq_map and 2 in freq_map:
            three = freq_map[3][0]
            two = freq_map[2][0]
            combo_cards = select_cards_for_values([three, two], {three: 3, two: 2})
            return hand("Фул-Хаус", 7, [three, two], combo_cards)

        elif flush_suit:
            combo_cards = flush_cards[:5]
            values = [rank_order[c.rank] for c in combo_cards]
            return hand("Флеш", 6, values, combo_cards)

        elif is_straight_all:
            combo_cards = []
            for v in straight_vals:
                for c in sorted(cards, key=lambda c: rank_order[c.rank], reverse=True):
                    if rank_order[c.rank] == v and c not in combo_cards:
                        combo_cards.append(c)
                        break
            return hand("Стрит", 5, straight_vals, combo_cards)

        elif 3 in freq_map:
            three = freq_map[3][0]
            combo_cards = select_cards_for_values([three], {three: 3})
            return hand("Тройка", 4, [three], combo_cards)

        elif 2 in freq_map and len(freq_map[2]) >= 2:
            pair1, pair2 = freq_map[2][:2]
            combo_cards = select_cards_for_values([pair1, pair2], {pair1: 2, pair2: 2})
            return hand("Две Пары", 3, [pair1, pair2], combo_cards)

        elif 2 in freq_map:
            pair = freq_map[2][0]
            combo_cards = select_cards_for_values([pair], {pair: 2})
            return hand("Пара", 2, [pair], combo_cards)

        else:
            combo_cards = sorted(cards, key=lambda c: rank_order[c.rank], reverse=True)[:1]
            values = [rank_order[combo_cards[0].rank]]
            return hand("Старшая Карта", 1, values, combo_cards)

    def start_game(self, n=6):
        CardGame.start_game(self)
        if self.us_rules:
            self.state = "player_give" if self.first_player == self.player else "opponent_give"

    def opponent_move(self):
        if not self.us_rules:
            return self.opponent.choose_attack_index(self.player.hand)
        else:
            return self.opponent.choose_card_to_give_away()

    def game_over(self):
        p1 = self._evaluate_hand(self.player.hand)
        p2 = self._evaluate_hand(self.opponent.hand)

        if (p1[1], p1[2]) > (p2[1], p2[2]):
            self.result = self.player.name
        elif (p1[1], p1[2]) < (p2[1], p2[2]):
            self.result = self.opponent.name
        else:
            self.result = "draw"

        return self.result, p1, p2