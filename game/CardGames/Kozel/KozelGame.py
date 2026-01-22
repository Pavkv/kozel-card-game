# coding=utf-8

from CardGames.Classes.CardGame import CardGame
from CardGames.Classes.Table import Table
from CardGames.Classes.Card import Card
from AIKozel import AIKozel

class KozelGame(CardGame):
    def __init__(self, player_name, opponent_name, biased_draw, full_deck, number_of_opponents=1):
        CardGame.__init__(self, player_name, biased_draw, full_deck=full_deck)

        self.number_of_opponents = number_of_opponents

        for i in range(number_of_opponents):
            if number_of_opponents == 1:
                name = opponent_name
            else:
                name = "{} {}".format(opponent_name, i + 1)

            ai = AIKozel(name)
            self.players.append(ai)

        self.table = Table(qualifier="suit")
        self.players_points = [0 for _ in range(len(self.players))]
        self.initial_attacker_index = None
        self.last_attacker = None

    def _count_total_points(self, player):
        """Count total points in player's discard pile."""
        total = 0
        for c in player.discard:
            pts = Card.points_kozel_map[c.rank]
            total += pts
        return total

    def count_total_points(self):
        """Count total points for all players."""
        for i, player in enumerate(self.players):
            self.players_points[i] = self._count_total_points(player)

    def sort_players_by_hand_suit(self):
        """Sort each player's hand by suit, with trump suit last."""
        for player in self.players:
            player.sort_hand_by_suit(self.deck.trump_suit)

    def is_player_last(self):
        """Check if the initial attacker is the next to play."""
        next_player_index = self.get_player_index(self.next_player())
        
        return next_player_index == self.initial_attacker_index

    def take_cards(self, receiver):
        """Player takes all cards from the table and the discard pile."""
        for atk_card, (beaten, def_card) in self.table.table.items():
            receiver.discard.append(atk_card)
            if def_card:
                receiver.discard.append(def_card)

        if self.deck.discard:
            for i in range(len(self.deck.discard)):
                receiver.discard.append(self.deck.discard.pop(0))

    def start_game(self, n=6, sort_hand=True, last_winner=None, first_player_selection="lowest_trump"):
        """Start the game by dealing cards and setting the initial attacker."""
        CardGame.start_game(self, n=n, sort_hand=sort_hand, last_winner=last_winner, first_player_selection=first_player_selection)
        self.initial_attacker_index = self.get_player_index(self.first_player)
        self.last_attacker = self.first_player

    def can_attack(self, attacker, num_of_attack_cards=0):
        """Check if the attacker can attack."""
        if len(attacker.hand) == 0:
            return False

        defender = self.next_player(self.get_player_index(attacker))

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
        attacker = self.current_turn
        defender = self.next_player(self.get_player_index(attacker))

        cards = attacker.choose_attack_cards(
            self.table,
            self.deck.trump_suit,
            len(defender.hand)
        )

        return cards

    def check_endgame(self):
        """Check if the game is over and set the result."""

        if self.deck.cards or self.player.hand:
            return

        self.count_total_points()
        max_points = max(self.players_points)
        winners = [i for i, pts in enumerate(self.players_points) if pts == max_points]
        if len(winners) > 1:
            self.result = "draw"
        else:
            self.result = self.players[winners[0]].name

    # Achievement checks
    def same_suit(self):
        """Check if all cards in player's hand are of the same suit."""
        if len(self.player.hand) < 6 or self.all_trumps():
            return False
        first_suit = self.player.hand[0].suit
        for card in self.player.hand:
            if card.suit != first_suit:
                return False
        return True

    def all_trumps(self):
        """Check if all cards in player's hand are trumps."""
        if len(self.player.hand) < 6:
            return False
        for card in self.player.hand:
            if card.suit != self.deck.trump_suit:
                return False
        return True

    def three_aces(self):
        """Check if player has three aces."""
        aces = [card for card in self.player.hand if card.rank == 'A']
        return len(aces) >= 3

    def three_sixes(self):
        """Check if player has three sixes."""
        sixes = [card for card in self.player.hand if card.rank == '6']
        return len(sixes) >= 3
