# coding=utf-8

from CardGames.Classes.CardGame import CardGame
from CardGames.Classes.Table import Table
from CardGames.Classes.Card import Card
from AIDurak import AIDurak

class DurakGame(CardGame):
    def __init__(self, player_name, opponent_name, biased_draw, full_deck, full_throw, can_pass, number_of_opponents=1):
        CardGame.__init__(self, player_name, biased_draw, full_deck=full_deck)

        self.number_of_opponents = number_of_opponents

        for i in range(number_of_opponents):
            if number_of_opponents == 1:
                name = opponent_name
            else:
                name = "{} {}".format(opponent_name, i + 1)

            ai = AIDurak(name)
            self.players.append(ai)

        self.table = Table()
        self.full_throw = full_throw
        self.can_pass = can_pass
        self.current_defender = None
        self.initial_attacker_index = None
        self.last_attacker = None

    def start_game(self, n=6, sort_hand=True, last_winner=None, first_player_selection="lowest_trump"):
        """Start the Durak game by dealing cards and setting the first player."""
        CardGame.start_game(self, n=n, sort_hand=sort_hand, last_winner=last_winner, first_player_selection=first_player_selection)
        self.initial_attacker_index = self.get_player_index(self.first_player)
        self.last_attacker = self.first_player
        self.current_defender = self.next_player(self.get_player_index(self.current_turn))

    def can_attack(self, attacker, num_of_attack_cards=0):
        """Check if the attacker can attack."""
        if len(attacker.hand) == 0:
            return False

        attacker_index = self.get_player_index(attacker)
        defender = self.next_player(attacker_index)

        if self.table.num_unbeaten() + num_of_attack_cards > len(defender.hand):
            return False

        if not self.full_throw and len(self.table) + num_of_attack_cards > 6:
            return False

        if len(self.table) == 0:
            return len(attacker.hand) > 0

        for card in attacker.hand:
            if card.rank in self.table.qualifier_set:
                return True

        return False

    def defend_card(self, defend_card, attack_card):
        """Player defends against an attack card."""
        if not Card.beats(defend_card, attack_card, self.deck.trump_suit):
            return False
        return True

    def opponent_attack(self):
        """Opponent chooses attack cards."""
        attacker = self.current_turn
        defender = self.current_defender
        cards = attacker.choose_attack_cards(
            self.table,
            self.deck.trump_suit,
            len(defender.hand),
            self.full_throw
        )

        if not cards:
            return False, []
        return True, cards

    def check_endgame(self):
        """Check if the game has ended and set the result."""
        if self.deck.cards:
            return

        active = self.get_players_with_cards()

        if len(active) == 0:
            self.result = "draw"
        elif len(active) == 1:
            self.result = active[0].name

    def check_for_loss_to_two_sixes(self):
        """Check for special achievements."""
        attack_cards = [atk for atk, (_b, _d) in self.table.table.items()]
        last_attack_two_sixes = (
            len(attack_cards) == 2
            and all(getattr(c, "rank", None) in ("6", 6) for c in attack_cards)
        )
        return len(self.players[1].hand) == 0 and last_attack_two_sixes