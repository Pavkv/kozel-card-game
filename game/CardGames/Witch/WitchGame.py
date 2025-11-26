# -*- coding: utf-8 -*-

from CardGames.Classes.CardGame import CardGame
from AIWitch import AIWitch


class WitchGame(CardGame):
    def __init__(self, player_name, opponent_name, biased_draw):
        CardGame.__init__(self, player_name, biased_draw)
        self.opponent = AIWitch(opponent_name)
        self.user_turn = None

    def start_game(self, n=6, sort_hand=False, first_player_selection=False):
        CardGame.start_game(self)
        if self.current_turn == self.player:
            self.player_turn_start()

    def player_turn_start(self):
        """
        Entry point for the player's turn.
        Returns the name of the button the player should press first:
        - "draw"
        - "discard_pairs"
        - "exchange"
        - "end_turn"
        """
        player = self.player
        deck = self.deck

        if len(player.hand) < 6 and len(deck.cards) > 0:
            self.user_turn = "draw"
        elif player.count_pairs_excluding_witch() > 0:
            self.user_turn = "discard_pairs"
        elif player.can_exchange_now(deck) and len(self.opponent.hand) > 0:
            self.user_turn = "exchange"
        else:
            self.user_turn = "end_turn"

    def game_over(self):
        if len(self.player.hand) == 0 and len(self.opponent.hand) > 1 and self.deck.is_empty():
            return True, self.player.name
        if len(self.opponent.hand) == 0 and len(self.player.hand) > 1 and self.deck.is_empty():
            return True, self.opponent.name
        if len(self.player.hand) == 1 and len(self.opponent.hand) == 1:
            if self.player.has_only_witch():
                return True, self.opponent.name
            if self.opponent.has_only_witch():
                return True, self.player.name
        return False, None
