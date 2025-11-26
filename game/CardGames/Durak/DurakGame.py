# coding=utf-8

from CardGames.Classes.CardGame import CardGame
from CardGames.Classes.Table import Table
from CardGames.Classes.Card import Card
from AIDurak import AIDurak

class DurakGame(CardGame):
    def __init__(self, player_name, opponent_name, biased_draw, full_deck, full_throw):
        CardGame.__init__(self, player_name, biased_draw, full_deck=full_deck)
        self.opponent = AIDurak(opponent_name)
        self.table = Table()
        self.full_throw = full_throw

    def start_game(self, n=6, sort_hand=True):
        CardGame.start_game(self, n=n, sort_hand=sort_hand)

    def can_attack(self, attacker, num_of_attack_cards=0):
        """Check if the attacker can attack."""
        if len(attacker.hand) == 0:
            return False

        defender = self.player if attacker is self.opponent else self.opponent

        if self.table.num_unbeaten() + num_of_attack_cards > len(defender.hand):
            return False
        if not self.full_throw and len(self.table) + num_of_attack_cards > 6:
            return False

        if len(self.table) == 0:
            return len(attacker.hand) > 0

        return any(card.rank in self.table.qualifier_set for card in attacker.hand)

    def defend_card(self, defend_card, attack_card):
        """Player defends against an attack card."""
        if not Card.beats(defend_card, attack_card, self.deck.trump_suit):
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

    def throw_ins(self):
        """Opponent throws in additional cards after beating all attacks."""
        throw_ins = self.opponent.choose_throw_ins(
            self.table,
            len(self.player.hand),
            self.deck.trump_suit
        )

        if self.full_throw:
            # Limit throw-ins so total cards on table do not exceed 6
            max_throw_ins = max(0, 6 - len(self.table))
            return throw_ins[:max_throw_ins]
        else:
            return throw_ins

    def check_endgame(self):
        """Check if the game is over and set the result."""
        if self.deck.cards or (len(self.player.hand) > 0 and len(self.opponent.hand) > 0):
            return
        player_cards = len(self.player.hand)
        opponent_cards = len(self.opponent.hand)
        if player_cards == 0 and player_cards == opponent_cards and self.table.beaten():
            self.result = "draw"
        elif player_cards < opponent_cards:
            self.result = self.player.name
        else:
            self.result = self.opponent.name


    def check_for_loss_to_two_sixes(self):
        """Check for special achievements."""
        # Get list of attack cards from the table
        attack_cards = [atk for atk, (_b, _d) in self.table.table.items()]

        # Check if last attack was two sixes and it's the last round
        last_attack_two_sixes = (
            len(attack_cards) == 2
            and all(getattr(c, "rank", None) in ("6", 6) for c in attack_cards)
        )

        return len(self.opponent.hand) == 0 and last_attack_two_sixes