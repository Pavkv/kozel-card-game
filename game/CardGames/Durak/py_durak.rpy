init python:
    # --------------------
    # Durak Animations
    # --------------------
    def durak_player_draw():
        draw_anim(side=0, sort_hand=True)

    def durak_opponent_draw():
        draw_anim(side=1, sort_hand=True)

    def durak_resolve_table_logic(is_beaten, receiver):
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
            draw_anim(side=0, sort_hand=True, on_finish="durak_opponent_draw")
        else:
            draw_anim(side=1, sort_hand=True, on_finish="durak_player_draw")

        card_game.player.sort_hand(card_game.deck.trump_suit)
        card_game.opponent.sort_hand(card_game.deck.trump_suit)

        compute_hand_layout()

    def durak_animate_and_resolve_table(step_delay=0.05, anim_duration=0.1):
        """
        Animate cards being cleared from the table and defer logic until after animation.
        """
        global hovered_card_index

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

        show_anim(
            on_finish="durak_resolve_table_logic",
            args=(is_beaten, receiver),
        )

        hovered_card_index = -1

    # --------------------
    # Player Functions
    # --------------------
    def durak_handle_card_click(index):
        """Handles card click events for player actions."""
        global confirm_attack, can_pass, passed, selected_attack_card_indexes, selected_attack_card

        card = card_game.player.hand[index]
        print("Card clicked:", card)

        # Player attack phase
        if card_game.state in ["player_turn", "opponent_take"] or (card_game.table.can_pass() and card.rank == card_game.table.keys()[0].rank and not passed):
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
            can_pass = (
                len(selected_attack_card_indexes) > 0
                and len(selected_attack_card_indexes) + len(card_game.table) <= len(card_game.opponent.hand)
            )

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
            else:
                print("Invalid defense with:", card)
                selected_attack_card = None

            if card_game.table.beaten() and not card_game.can_attack(card_game.opponent):
                print("All attacks beaten. Player wins this round.")
                card_game.state = "end_turn"
                selected_attack_card = None

    def durak_player_switch_to_defend():
        global confirm_attack, can_pass, passed, selected_attack_card_indexes
        selected_attack_card_indexes.clear()
        confirm_attack = False
        can_pass = False
        if card_game.state == "opponent_take" and not card_game.can_attack(card_game.player):
            card_game.state = "end_turn"
        elif card_game.state == "opponent_take":
            card_game.state == "player_turn"
        else:
            if card_game.state == "player_defend":
                card_game.current_turn = card_game.player
                passed = True
            card_game.state = "opponent_defend"

    def durak_confirm_selected_attack():
        """Confirms all selected attack cards and animates them from hand to table."""
        global confirm_attack, can_pass, selected_attack_card_indexes

        if (confirm_attack or can_pass) and selected_attack_card_indexes:
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
                    on_finish="durak_player_switch_to_defend"
                )
            elif card_game.table.can_pass():
                print("Player transferred attack with: " + ', '.join(str(c) for c in cards))

                # Animate each card moving to table
                start_index = len(card_game.table)
                play_card_anim(
                    cards=cards,
                    side=0,
                    slot_index=start_index,
                    is_defense=False,
                    on_finish="durak_player_switch_to_defend"
                )
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

                card_game.state = "player_defend" if not confirm_take else "end_turn"

            else:
                print("AI attempted to attack but failed unexpectedly.")
                card_game.state = "end_turn"

        else:
            if not card_game.table.beaten() and not confirm_take:
                print("AI skipped attack; player must still defend or take.")
                card_game.state = "player_defend"

            else:
                print("AI cannot attack and table is beaten. Ending turn.")
                card_game.state = "end_turn"

    def durak_opponent_defend():
        """Handles the opponent's defense logic sequentially with animation."""
        global durak_defense_queue, durak_defense_index, passed

        if card_game.table.can_pass() and len(card_game.player.hand) >= len(card_game.table) + 1 and not passed:
            should_transfer, transfer_card = card_game.opponent.should_transfer(
                card_game.table,
                card_game.deck.trump_suit
            )

            if should_transfer:
                print("AI chooses to transfer using:", transfer_card)

                card_game.opponent.hand.remove(transfer_card)
                card_game.table.append(transfer_card)

                play_card_anim(
                    cards=[transfer_card],
                    side=1,
                    slot_index=len(card_game.table) - 1,
                    is_defense=False,
                    delay=0.0
                )

                card_game.state = "player_defend"
                card_game.current_turn = card_game.opponent
                passed = True
                return

        durak_defense_queue = []
        reserved_cards = set()

        for i, (attack_card, (beaten, _)) in enumerate(card_game.table.table.items()):
            if not beaten:
                def_card = card_game.opponent.defense(
                    attack_card,
                    card_game.deck.trump_suit,
                    exclude=reserved_cards
                )
                if def_card:
                    durak_defense_queue.append((i, attack_card, def_card))
                    reserved_cards.add(def_card)
                else:
                    print("AI cannot defend against:", attack_card)
                    break

        durak_defense_index = 0

        if durak_defense_queue:
            durak_opponent_do_defense()
        else:
            print("AI could not defend. Will need to take.")
            card_game.state = "opponent_take" if card_game.can_attack(card_game.player) else "end_turn"

    def durak_opponent_do_defense():
        """Executes one defense step at a time using animation + show_anim."""
        global durak_defense_queue, durak_defense_index

        if durak_defense_index >= len(durak_defense_queue):
            # Done with all defenses
            if card_game.table.beaten():
                print("AI defended all attacks.")
                card_game.state = "player_turn" if card_game.can_attack(card_game.player) else "end_turn"
            else:
                print("AI failed to defend completely.")
                card_game.state = "opponent_take" if card_game.can_attack(card_game.player) else "end_turn"
            return

        slot_index, atk_card, def_card = durak_defense_queue[durak_defense_index]

        play_card_anim(
            cards=[def_card],
            side=1,
            slot_index=slot_index,
            is_defense=True,
            delay=0.0
        )

        # Wait for animation, then continue logic
        show_anim(
            on_finish="durak_opponent_apply_defense"
        )

    def durak_opponent_apply_defense():
        """Applies the current defense step and continues to the next."""
        global durak_defense_queue, durak_defense_index

        slot_index, atk_card, def_card = durak_defense_queue[durak_defense_index]

        print("AI defends", atk_card, "with", def_card)
        card_game.table.beat(atk_card, def_card)
        if def_card in card_game.opponent.hand:
            card_game.opponent.hand.remove(def_card)
        compute_hand_layout()

        # Next step
        durak_defense_index += 1
        durak_opponent_do_defense()

    # --------------------
    # End Turn Logic
    # --------------------
    def durak_end_turn():
        global confirm_take, passed

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
        passed = False

    # --------------------
    # Animation Callbacks
    # --------------------
    def resolve_on_finish(key):
        if key == "durak_player_draw":
            durak_player_draw()
        elif key == "durak_opponent_draw":
            durak_opponent_draw()
        elif key == "durak_resolve_table_logic":
            durak_resolve_table_logic()
        elif key == "durak_player_switch_to_defend":
            durak_player_switch_to_defend()
        elif key == "durak_opponent_apply_defense":
            durak_opponent_apply_defense()