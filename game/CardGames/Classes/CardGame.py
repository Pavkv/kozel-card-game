# coding=utf-8
import random

from Card import Card
from Player import Player
from Deck import Deck

class CardGame:
    def __init__(self, player_name="Вы", biased_draw=None, aces_low=False, full_deck=False, num_ai_opponents=1):
        Card.set_deck_type(use_full_deck=full_deck)
        self.deck = Deck()

        # Player 0 is ALWAYS human
        self.players = [Player(player_name, aces_low)]
        self.player = self.players[0]
        self.opponent = None

        self.first_player = None
        self.current_turn = None
        self.state = None
        self.result = None

        self.bias = {"player": 0.0, "opponent": 0.0}
        if biased_draw:
            who, amount = biased_draw
            self.bias[who] = float(amount)

    def deal_cards(self, n=6, sort_hand=False):
        for i, player in enumerate(self.players):
            bias = self.bias["player"] if i == 0 else self.bias["opponent"]
            player.draw_from_deck(self.deck, n, sort_hand, bias)

    def select_first_player(self, first_player_selection=None):
        if first_player_selection == "player":
            self.first_player = self.players[0]
        elif first_player_selection == "opponent":
            self.first_player = self.players[1]
        elif first_player_selection == "lowest_trump":
            lowest_trump_player = None
            lowest_trump_card = None

            for player in self.players:
                card = player.lowest_trump_card(self.deck.trump_suit)
                if card and (lowest_trump_card is None or card < lowest_trump_card):
                    lowest_trump_card = card
                    lowest_trump_player = player

            self.first_player = lowest_trump_player if lowest_trump_player else random.choice(self.players)
        else:
            self.first_player = random.choice(self.players)

    def start_game(self, n=6, sort_hand=False):
        self.opponent = self.players[1]
        self.deal_cards(n, sort_hand)
        self.current_turn = self.first_player
        self.state = "player_turn" if self.first_player == self.players[0] else "opponent_turn"