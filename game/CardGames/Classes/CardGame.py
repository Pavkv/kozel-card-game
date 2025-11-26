# coding=utf-8
import random

from Card import Card
from Player import Player
from Deck import Deck

class CardGame:
    def __init__(self, player_name="Вы", biased_draw=None, aces_low=False, full_deck=False):
        Card.set_deck_type(use_full_deck=full_deck)
        self.deck = Deck()
        self.player = Player(player_name, aces_low)
        self.opponent = None
        self.first_player = None
        self.current_turn = None
        self.state = None
        self.result = None

        self.bias = {"player": 0.0, "opponent": 0.0}
        if biased_draw:
            if biased_draw[0] == "player":
                self.bias["player"] = float(biased_draw[1])
            elif biased_draw[0] == "opponent":
                self.bias["opponent"] = float(biased_draw[1])

    def select_first_player(self, first_player_selection=None):
        if first_player_selection == "player":
            self.first_player = self.player
        elif first_player_selection == "opponent":
            self.first_player = self.opponent
        elif first_player_selection == "lowest_trump":
            player_trump = self.player.lowest_trump_card(self.deck.trump_suit)
            opponent_trump = self.opponent.lowest_trump_card(self.deck.trump_suit)
            if player_trump and (not opponent_trump or player_trump < opponent_trump):
                self.first_player = self.player
            else:
                self.first_player = self.opponent
        else:
            self.first_player = random.choice([self.player, self.opponent])

    def start_game(self, n=6, sort_hand=False):
        self.player.draw_from_deck(self.deck, n, sort_hand, self.bias["player"])
        self.opponent.draw_from_deck(self.deck, n, sort_hand, self.bias["opponent"])
        self.state = "player_turn" if self.first_player == self.player else "opponent_turn"
        self.current_turn = self.first_player