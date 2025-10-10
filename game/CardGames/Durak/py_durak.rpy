init python:
     # --------------------
     # Durak Animations
     # --------------------
    def durak_animate_and_resolve_table(step_delay=0.05, anim_duration=0.1):
        global hovered_card_index
        """
        Animate cards being cleared from the table and defer logic until after animation.
        """

        table_animations[:] = []
        delay = 0.0

        is_beaten = card_game.table.beaten()

        receiver = (
            card_game.player
            if card_game.current_turn != card_game.player
            else card_game.opponent
        )

        for i, (atk_card, (beaten, def_card)) in enumerate(card_game.table.table.items()):
            src_x = 350 + i * 200
            src_y = 375
            cards = list(filter(None, [atk_card, def_card]))

            for card in cards:
                offset_x = 30 * i
                offset_y = 0

                anim = {
                    "card": card,
                    "src_x": src_x,
                    "src_y": src_y if card == atk_card else src_y + 120,
                    "delay": delay,
                    "duration": anim_duration,
                }

                if is_beaten:
                    anim.update({
                        "dest_x": 1600 + offset_x,
                        "dest_y": 350 + offset_y,
                        "target": "discard",
                    })
                else:
                    anim.update({
                        "dest_x": 700 + offset_x,
                        "dest_y": 825 if receiver == card_game.player else 20,
                        "target": "hand",
                    })

                table_animations.append(anim)
                delay += step_delay

        def resolve_table_logic():
            if is_beaten:
                for atk_card, (beaten, def_card) in card_game.table.table.items():
                    card_game.deck.discard.append(atk_card)
                    if def_card:
                        card_game.deck.discard.append(def_card)
                card_game.current_turn = (
                    card_game.opponent if card_game.current_turn == card_game.player else card_game.player
                )
                card_game.state = (
                    "player_turn" if card_game.current_turn == card_game.player else "opponent_turn"
                )
            else:
                for atk_card, (beaten, def_card) in card_game.table.table.items():
                    receiver.hand.append(atk_card)
                    if def_card:
                        receiver.hand.append(def_card)
                card_game.state = (
                    "player_turn" if receiver == card_game.opponent else "opponent_turn"
                )

            card_game.table.clear()

            print("Discard pile:", card_game.deck.discard)
            print("Player hand after turn:", card_game.player.hand)
            print("Opponent hand after turn:", card_game.opponent.hand)

            if card_game.current_turn == card_game.opponent:
                draw_anim(side=0, sort_hand=True, on_finish=lambda: draw_anim(side=1, sort_hand=True))
            else:
                draw_anim(side=1, sort_hand=True, on_finish=lambda: draw_anim(side=0, sort_hand=True))

            card_game.player.sort_hand(card_game.deck.trump_suit)
            card_game.opponent.sort_hand(card_game.deck.trump_suit)

            compute_hand_layout()

        show_anim(function=resolve_table_logic)

        hovered_card_index = -1

    # --------------------
    # Player Functions
    # --------------------
    def durak_handle_card_click(index):
        """Handles card click events for player actions."""
        global confirm_attack, selected_attack_card_indexes, selected_attack_card

        card = card_game.player.hand[index]
        print("Card clicked:", card)

        # Player attack phase
        if card_game.state == "player_turn":
            if index in selected_attack_card_indexes:
                selected_attack_card_indexes.remove(index)
                print("Unselected:", card)
            else:
                # Allow selecting if first or same rank as already selected
                allowed_ranks = {card_game.player.hand[i].rank for i in selected_attack_card_indexes}
                if not selected_attack_card_indexes or card.rank in allowed_ranks:
                    selected_attack_card_indexes.add(index)
                    print("Selected:", card)

            confirm_attack = len(selected_attack_card_indexes) > 0

        # Player defend phase
        elif card_game.state == "player_defend" and selected_attack_card:
            if card_game.defend_card(card, selected_attack_card):
                print("Player defended against {} with {}".format(selected_attack_card, card))

                # Animate defense card going to table
                table_size = len(card_game.table)
                attack_slot_index = next((i for i, (atk, _) in enumerate(card_game.table.table.items()) if atk == selected_attack_card), table_size - 1)

                play_card_anim(
                    cards=[card],
                    side=0,
                    slot_index=attack_slot_index,
                    is_defense=True,
                )

                selected_attack_card = None
                card_game.state = "opponent_turn"
            else:
                print("Invalid defense with:", card)
                selected_attack_card = None

    def durak_confirm_selected_attack():
        """Confirms all selected attack cards and animates them from hand to table."""
        global confirm_attack, selected_attack_card_indexes

        if confirm_attack and selected_attack_card_indexes:
            indexes = sorted(selected_attack_card_indexes)
            cards = [card_game.player.hand[i] for i in indexes]

            if card_game.can_attack(card_game.player):
                print("Player attacked with: " + ', '.join(str(c) for c in cards))

                # Animate each card moving to table
                start_index = len(card_game.table)
                play_card_anim(
                    cards=cards,
                    side=0,
                    slot_index=start_index,
                    is_defense=False,
                )

                # Clear selection and proceed to opponent turn
                selected_attack_card_indexes.clear()
                confirm_attack = False
                card_game.state = "opponent_defend"

            else:
                print("Invalid attack. Resetting selection.")
                selected_attack_card_indexes.clear()
                confirm_attack = False

    # --------------------
    # Opponent Functions
    # --------------------
    def durak_opponent_turn():
        """Handles opponent's attack selection logic."""
        global confirm_take

        if card_game.can_attack(card_game.opponent):
            attack_success, cards = card_game.opponent_attack()
            if attack_success:
                print("AI attacked successfully with:", cards)

                start_index = len(card_game.table)
                play_card_anim(
                    cards=cards,
                    side=1,
                    slot_index=start_index,
                    is_defense=False,
                )

                card_game.state = "player_defend"

            else:
                print("AI attempted to attack but failed unexpectedly.")
                card_game.state = "end_turn"

        else:
            if not card_game.table.beaten() and not confirm_take:
                print("AI skipped attack; player must still defend or take.")
                card_game.state = "player_defend"

            else:
                print("AI cannot attack and table is beaten. Ending turn.")
                confirm_take = False
                card_game.state = "end_turn"

    def durak_opponent_defend():
        """Handles the opponent's defense logic sequentially with animation."""
        defense_queue = []

        reserved_cards = set()

        for i, (attack_card, (beaten, _)) in enumerate(card_game.table.table.items()):
            if not beaten:
                def_card = card_game.opponent.defense(
                    attack_card,
                    card_game.deck.trump_suit,
                    exclude=reserved_cards
                )
                if def_card:
                    defense_queue.append((i, attack_card, def_card))
                    reserved_cards.add(def_card)  # Reserve this card
                else:
                    print("AI cannot defend against:", attack_card)
                    break

        def do_defense(index=0):
            if index >= len(defense_queue):
                # All done — now check if fully defended
                if card_game.table.beaten():
                    print("AI defended all attacks.")
                else:
                    print("AI failed to defend completely.")
                card_game.state = "player_turn"
                return

            slot_index, atk_card, def_card = defense_queue[index]

            def apply_defense():
                # Now it's safe to update the game state
                card_game.table.beat(atk_card, def_card)
                if def_card in card_game.opponent.hand:
                    card_game.opponent.hand.remove(def_card)
                compute_hand_layout()

                # Move to next defense
                do_defense(index + 1)

            # Animate it
            play_card_anim(
                cards=[def_card],
                side=1,
                slot_index=slot_index,
                is_defense=True,
                delay=0.0
            )
            show_anim(apply_defense)  # ensure `beat()` happens *after* animation

        if defense_queue:
            do_defense()
        else:
            print("AI could not defend. Will need to take.")
            card_game.state = "player_turn"

    # --------------------
    # End Turn Logic
    # --------------------
    def durak_end_turn():
        global confirm_take  # Ensure this resets the global flag

        # AI Throw-ins if it was the AI's turn and player still can be attacked
        if card_game.current_turn == card_game.opponent and card_game.can_attack(card_game.opponent):
            print("AI adding throw-ins.")
            throw_ins = card_game.throw_ins()

            table_animations[:] = []
            for i, card in enumerate(throw_ins):
                play_card_anim(
                    card=card,
                    side=1,
                    slot_index=len(card_game.table) - len(cards) + i,
                    is_defense=False,
                    delay=i * 0.1
                )

            show_anim()

        print("Table before ending turn:", card_game.table)
        print("Player hand before ending turn:", card_game.player.hand)
        print("Opponent hand before ending turn:", card_game.opponent.hand)

        # Lost to two sixes check
        if card_game.current_turn == card_game.opponent and card_game.deck.is_empty():
            lost_to_two_sixes = card_game.check_for_loss_to_two_sixes()
            if lost_to_two_sixes:
                print("You lost to two sixes in the last round!")

        card_game.opponent.remember_table(card_game.table)
        card_game.opponent.remember_discard(card_game.deck.discard)

        # Animate and resolve the table
        durak_animate_and_resolve_table()

        # Check for game over conditions
        card_game.check_endgame()

        # Check if game has ended
        if card_game.result:
            card_game.state = "result"
            return

        print("Player hand after drawing:", card_game.player.hand)
        print("Opponent hand after drawing:", card_game.opponent.hand)

        confirm_take = False
