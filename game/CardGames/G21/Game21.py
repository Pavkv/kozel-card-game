# coding=utf-8
from CardGames.Classes.CardGame import CardGame
from AI21 import AI21


class Game21(CardGame):
    def __init__(self, player_name, opponent_name, biased_draw, initial_deal, aces_low):
        CardGame.__init__(self, player_name, biased_draw, aces_low)
        self.players.append(AI21(opponent_name))
        self.initial_deal = initial_deal
        self.that_s_him = False  # special flag for "That’s him!" achievement
        self.all_in_place = False  # special flag for "All in place" achievement

    def _instant_check(self):
        if self.player.total21() == 21:
            self.finalize(winner=self.player)
            return True
        if self.opponent.total21() == 21:
            self.finalize(winner=self.opponent)
            return True
        return False

    def start_game(self, n=1, sort_hand=False, last_winner=None, first_player_selection=None):
        CardGame.start_game(self, n=self.initial_deal, sort_hand=sort_hand, last_winner=last_winner, first_player_selection=first_player_selection)
        self._instant_check()

    def opponent_turn(self):
        return self.opponent.decide(seen_cards=list(self.opponent.hand), opponent_total=self.player.total21())

    def finalize(self, winner=None):
        if winner is self.player:
            self.result = self.player.name
        elif winner is self.opponent:
            self.result = self.opponent.name
        else:
            ht, at = self.player.total21(), self.opponent.total21()
            hb, ab = self.player.is_bust21(), self.opponent.is_bust21()
            if hb and ab:
                self.result = "draw"
            elif hb:
                self.result = self.opponent.name
            elif ab:
                self.result = self.player.name
            elif ht == at:
                self.result = "draw"
            elif ht > at:
                self.result = self.player.name
            else:
                self.result = self.opponent.name
