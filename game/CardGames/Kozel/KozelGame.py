# coding=utf-8

from game.CardGames.Classes.CardGame import CardGame
from game.CardGames.Classes.AIKozel import AIKozel
from game.CardGames.Classes.Table import Table
from game.CardGames.Classes.Card import Card

class KozelGame(CardGame):
    def __init__(self, player_name, opponent_name, biased_draw):
        CardGame.__init__(self, player_name, biased_draw)
        self.opponent = AIKozel(opponent_name)
        self.table = Table(qualifier="suit")
        self.player_points = 0
        self.opponent_points = 0

    def _count_total_points_kozel(self, player):
        total = 0
        for c in player.discard:
            pts = Card.points_kozel_map[c.rank]
            total += pts
        return total

    def count_total_points_kozel_both(self):
        self.player_points = self._count_total_points_kozel(self.player)
        self.opponent_points = self._count_total_points_kozel(self.opponent)

    def take_cards(self, receiver):
        for atk_card, (beaten, def_card) in self.table.table.items():
            receiver.discard.append(atk_card)
            if def_card:
                receiver.discard.append(def_card)

    def start_game(self, n=6, sort_hand=True):
        CardGame.start_game(self, n=n, sort_hand=sort_hand)

    def can_attack(self, attacker, num_of_attack_cards=0):
        """Check if the attacker can attack."""
        if len(attacker.hand) == 0:
            return False

        defender = self.player if attacker is self.opponent else self.opponent

        if num_of_attack_cards > len(defender.hand):
            return False

        if len(self.table) == 0:
            return len(attacker.hand) > 0

        return True

    def defend_card(self, defend_card, attack_card):
        """Player defends against an attack card."""
        if not Card.beats_kozel(defend_card, attack_card, self.deck.trump_suit):
            return False
        return True

    def opponent_attack(self):
        """Opponent attacks with chosen cards."""
        cards = self.opponent.choose_attack_cards(
            self.table,
            self.deck.trump_suit,
            len(self.player.hand)
        )
        if not cards:
            return False, []
        else:
            return True, cards

    def check_endgame(self):
        """Check if the game is over and set the result."""
        if self.deck.cards or (len(self.player.hand) > 0 and len(self.opponent.hand) > 0):
            return
        self.count_total_points_kozel_both()
        if self.player_points == self.opponent_points:
            self.result = "draw"
        elif self.player_points > self.opponent_points:
            self.result = self.player.name
        else:
            self.result = self.opponent.name