# coding=utf-8
import random

from Card import Card
from Player import Player
from Deck import Deck

class CardGame:
    def __init__(self, player_name="Вы", biased_draw=None, aces_low=False, full_deck=False):
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

    def get_player_index(self, player):
        """Get the index of a player in the circle."""
        return self.players.index(player)

    def next_player(self, index=None):
        """Get the next player in the circle."""
        if index is None:
            index = self.get_player_index(self.current_turn)
        return self.players[(index + 1) % len(self.players)]

    def previous_player(self, index=None):
        """Get the previous player in the circle."""
        if index is None:
            index = self.get_player_index(self.current_turn)
        return self.players[(index - 1) % len(self.players)]

    def get_players_with_cards(self):
        """Get a list of players who still have cards in their hands."""
        return [player for player in self.players if len(player.hand) > 0]

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
                if card is None:
                    continue

                if (
                        lowest_trump_card is None or
                        Card.rank_values[card.rank] < Card.rank_values[lowest_trump_card.rank]
                ):
                    lowest_trump_card = card
                    lowest_trump_player = player

            self.first_player = lowest_trump_player if lowest_trump_player else random.choice(self.players)
        else:
            self.first_player = random.choice(self.players)

    def start_game(self, n=6, sort_hand=False, last_winner=None, first_player_selection=None):
        self.opponent = self.players[1]
        self.deal_cards(n, sort_hand)
        if last_winner:
            self.select_first_player(last_winner)
        else:
            self.select_first_player(first_player_selection)
        self.current_turn = self.first_player
        self.state = "player_turn" if self.first_player == self.players[0] else "opponent_turn"