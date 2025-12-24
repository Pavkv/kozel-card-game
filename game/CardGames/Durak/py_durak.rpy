init python:
    # --------------------
    # Support Functions
    # --------------------
    def durak_get_defender():
        if card_game.get_player_index(card_game.current_defender) == 0:
            card_game.state = "player_defend"
        else:
            card_game.state = "opponent_defend"

    def durak_can_attack():
        defender_index = card_game.get_player_index(card_game.current_defender)
        previous_player = card_game.previous_player(defender_index)
        next_player = card_game.next_player(defender_index)
        return card_game.can_attack(previous_player) or card_game.can_attack(next_player)

    def durak_get_next_attacker():
        global confirm_turn

        defender_index = card_game.get_player_index(card_game.current_defender)
        previous_player = card_game.previous_player(defender_index)
        next_player = card_game.next_player(defender_index)

        if len(card_game.current_defender.hand) == 0:
            print("Defender has no cards left. Ending turn.")
            card_game.state = "end_turn"
            return

        if (
            (not card_game.full_throw and len(card_game.table) >= 6) or
            (card_game.table.num_unbeaten() >= len(card_game.current_defender.hand)) or
            not durak_can_attack()
        ):
            print("Max throws reached or no one can attack. Ending turn.")
            card_game.state = "end_turn"
            return

        if confirm_turn[0] or confirm_turn[1]:
            if confirm_turn[0] and confirm_turn[1]:
                print("Both players confirmed turn end. Ending turn.")
                card_game.state = "end_turn"
                confirm_turn = [False, False]
                return
            if next_player == card_game.last_attacker and not card_game.can_attack(previous_player):
                print("Player was last attacker and is also next, but previous cannot attack. Ending turn.")
                card_game.state = "end_turn"
                return
            if previous_player == card_game.last_attacker and not card_game.can_attack(next_player):
                print("Player was last attacker and is also previous, but next cannot attack. Ending turn.")
                card_game.state = "end_turn"
                return
            if next_player == card_game.last_attacker and card_game.can_attack(previous_player):
                print("Player was last attacker and is also next. Switching to previous player.")
                card_game.current_turn = card_game.last_attacker = previous_player
            if previous_player == card_game.last_attacker and card_game.can_attack(next_player):
                print("Player was last attacker and is also previous. Switching to next player.")
                card_game.current_turn = card_game.last_attacker = next_player
            card_game.state = "player_turn" if card_game.get_player_index(card_game.current_turn) == 0 else "opponent_turn"
            return

        # Otherwise: try in order — last_attacker → next → previous
        if card_game.can_attack(card_game.last_attacker):
            print("Last attacker can attack again:", card_game.last_attacker)
            card_game.current_turn = card_game.last_attacker
        elif card_game.can_attack(next_player):
            print("Next player can attack:", next_player)
            card_game.current_turn = card_game.last_attacker = next_player
        elif card_game.can_attack(previous_player):
            print("Previous player can attack:", previous_player)
            card_game.current_turn = card_game.last_attacker = previous_player
        else:
            print("No players can attack. Ending turn.")
            card_game.state = "end_turn"
            return

        # Set state
        card_game.state = "player_turn" if card_game.get_player_index(card_game.current_turn) == 0 else "opponent_turn"
    
    # --------------------
    # Durak Animations
    # --------------------
    def durak_player_draw():
        on_finish = get_next_draw_side()
        draw_anim(side=0, sort_hand=True, on_finish=on_finish)

    def durak_opponent_draw():
        on_finish = get_next_draw_side()
        draw_anim(side=1, sort_hand=True, on_finish=on_finish)

    def durak_opponent_2_draw():
        on_finish = get_next_draw_side()
        draw_anim(side=2, sort_hand=True, on_finish=on_finish)

    def durak_opponent_3_draw():
        on_finish = get_next_draw_side()
        draw_anim(side=3, sort_hand=True, on_finish=on_finish)

    def durak_resolve_table_logic(is_beaten):
        print("Resolving table. Beaten:", is_beaten)
        print("Table before resolution:", card_game.table)
        print("Player hand before turn:", card_game.player.hand)
        for i in range(1, len(card_game.players)):
            print("Opponent {} hand before turn:{}", i, card_game.players[i].hand)

        receiver = card_game.current_defender
        receiver_index = card_game.get_player_index(receiver)

        # Move cards to discard or receiver’s hand
        if is_beaten:
            for atk_card, (beaten, def_card) in card_game.table.table.items():
                card_game.deck.discard.append(atk_card)
                if def_card:
                    card_game.deck.discard.append(def_card)
        else:
            for atk_card, (beaten, def_card) in card_game.table.table.items():
                receiver.hand.append(atk_card)
                if def_card:
                    receiver.hand.append(def_card)

        card_game.table.clear()

        active = card_game.get_players_with_cards()

        # Remove players with no cards left (after deck is empty)
        if len(card_game.deck.cards) == 0:
            print("Deck is empty after turn.")
            for p in list(active):  # safe copy for mutation
                if len(p.hand) == 0:
                    print("{} is out of cards and removed from active players.", p.name)
                    active.remove(p)

        # Advance to next attacker or defender
        if is_beaten:
            # Defender succeeded → defender becomes attacker (only if still active)
            next_attacker = receiver
        else:
            # Defender failed → next attacker (after receiver)
            next_attacker = card_game.next_player(receiver_index)

        # Skip players with no cards for attacker
        while len(next_attacker.hand) == 0:
            next_attacker = card_game.next_player(card_game.get_player_index(next_attacker))

        card_game.current_turn = card_game.last_attacker = next_attacker

        # Now set the next valid defender (player after current_turn with cards)
        next_defender = card_game.next_player(card_game.get_player_index(card_game.current_turn))
        while len(next_defender.hand) == 0:
            next_defender = card_game.next_player(card_game.get_player_index(next_defender))

        card_game.current_defender = next_defender

        # Set state
        if card_game.current_turn == card_game.player:
            card_game.state = "player_turn"
        else:
            card_game.state = "opponent_turn"

        print("Discard pile:", card_game.deck.discard)
        print("Player hand after turn:", card_game.player.hand)
        for i in range(1, len(card_game.players)):
            print("Opponent {} hand after turn:{}", i, card_game.players[i].hand)

        # Prepare draw animations
        for i in range(card_game.initial_attacker_index, len(card_game.players) + card_game.initial_attacker_index):
            p = card_game.players[i % len(card_game.players)]
            if p != receiver:
                on_finish_draw_animations.append(durak_draw_animations_dict[card_game.get_player_index(p)])

        # Receiver draws last
        on_finish_draw_animations.append(durak_draw_animations_dict[receiver_index])

        # Start the draw animations
        resolve_on_finish(on_finish_draw_animations.pop(0))

        # Sort all hands
        for i, p in enumerate(card_game.players):
            p.sort_hand(card_game.deck.trump_suit)

        card_game.initial_attacker_index = card_game.get_player_index(card_game.current_turn)

        compute_hand_layout()

    def durak_animate_and_resolve_table(step_delay=0.05, anim_duration=0.1):
        """
        Animate cards being cleared from the table and defer logic until after animation.
        """
        global hovered_card_index

        table_animations[:] = []
        delay = 0.0

        is_beaten = card_game.table.beaten()
        receiver = card_game.current_defender

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
                    })
                else:
                    anim.update({
                        "dest_x": hand_card_pos(card_game.get_player_index(receiver), card)[0],
                        "dest_y": hand_card_pos(card_game.get_player_index(receiver), card)[1],
                    })

                table_animations.append(anim)
                delay += step_delay

        show_anim(
            on_finish="durak_resolve_table_logic",
            args=(is_beaten,),
        )

        hovered_card_index = -1

    # --------------------
    # Player Functions
    # --------------------
    def durak_handle_card_click(index):
        """Handles card click events for player actions."""
        global confirm_attack, can_pass, selected_attack_card_indexes, selected_attack_card

        player = card_game.player
        defender = card_game.current_defender
        next_defender = card_game.next_player(0)

        card = player.hand[index]
        print("Card clicked:", card)

        # Player attack phase
        if card_game.state in ["player_turn", "opponent_take"] or (card_game.table.can_pass() and card.rank == card_game.table.keys()[0].rank and not selected_attack_card):
            if index in selected_attack_card_indexes:
                selected_attack_card_indexes.remove(index)
                print("Unselected:", card)
            else:
                # Allow selecting if first or same rank as already selected and ranks on the table
                if (
                    not selected_attack_card_indexes or
                    card.rank in card_game.table.qualifier_set or
                    card.rank in {card_game.player.hand[i].rank for i in selected_attack_card_indexes}
                ):
                    selected_attack_card_indexes.add(index)
                    print("Selected:", card)

            confirm_attack = (
                len(selected_attack_card_indexes) > 0
                and len(selected_attack_card_indexes) + len(card_game.table) <= len(defender.hand)
            )

            can_pass = (
                card_game.table.can_pass()
                and len(selected_attack_card_indexes) > 0
                and len(selected_attack_card_indexes) + len(card_game.table) <= len(next_defender.hand)
            )

        # Player defend phase
        elif card_game.state == "player_defend" and selected_attack_card:

            if card_game.defend_card(card, selected_attack_card):
                print("Player defended against {} with {}".format(selected_attack_card, card))

                confirm_turn = [False, False]

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

            if card_game.table.beaten() and not card_game.can_attack(player):
                print("All attacks beaten. Player wins this round.")
                card_game.state = "end_turn"
                selected_attack_card = None

    def durak_player_switch_to_defend():
        global confirm_attack, can_pass, selected_attack_card_indexes
        selected_attack_card_indexes.clear()
        confirm_attack = False
        can_pass = False
        if card_game.state == "opponent_take" and not durak_can_attack():
            card_game.state = "end_turn"
        elif card_game.state == "opponent_take":
            durak_get_next_attacker()
        else:
            if card_game.state == "player_defend":
                card_game.current_turn = card_game.last_attacker = card_game.player
                card_game.current_defender = card_game.next_player(0)
            card_game.state = "opponent_defend"

    def durak_confirm_selected_attack():
        """Confirms all selected attack cards and animates them from hand to table."""
        global confirm_attack, can_pass, selected_attack_card_indexes

        player = card_game.player
        print(confirm_attack)
        if (confirm_attack or can_pass) and selected_attack_card_indexes:
            indexes = sorted(selected_attack_card_indexes)
            cards = [player.hand[i] for i in indexes]

            if card_game.can_attack(player):
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
    def durak_opponent_after_turn():
        """Callback after opponent's turn animations complete."""
        print("AI completed attack. Moving to defender.")
        durak_get_defender()
        confirm_index = 0 if confirm_turn[0] is False and confirm_turn[1] else 1
        confirm_turn[confirm_index] = True

    def durak_opponent_turn():
        """Handles opponent's attack selection logic."""
        global confirm_take

        opponent = card_game.current_turn
        opponent_index = card_game.get_player_index(opponent)

        if card_game.can_attack(opponent):
            attack_success, cards = card_game.opponent_attack()
            if attack_success:
                print("AI attacked successfully with:", cards)

                start_index = len(card_game.table)
                play_card_anim(
                    cards=cards,
                    side=opponent_index,
                    slot_index=start_index,
                    is_defense=False,
                    on_finish="durak_opponent_after_turn"
                )
            else:
                durak_opponent_after_turn()

        else:
            confirm_index = 0 if confirm_turn[0] is False and confirm_turn[1] else 1
            confirm_turn[confirm_index] = True
            if not card_game.table.beaten() and not confirm_take:
                print("AI skipped attack; table not beaten.")
                durak_get_defender()
            else:
                print("AI cannot attack and table is beaten.")
                durak_get_next_attacker()

    def durak_opponent_defend():
        """Handles the opponent's defense logic sequentially with animation."""
        global durak_defense_queue, durak_defense_index

        opponent = card_game.current_defender
        opponent_index = card_game.get_player_index(opponent)

        # Handle transfer logic
        if card_game.table.can_pass() and len(card_game.next_player(opponent_index).hand) >= len(card_game.table) + 1:
            should_transfer, transfer_card = opponent.should_transfer(
                card_game.table,
                card_game.deck.trump_suit
            )
            if should_transfer:
                print("AI chooses to transfer using:", transfer_card)
                opponent.hand.remove(transfer_card)
                card_game.table.append(transfer_card)
                play_card_anim(
                    cards=[transfer_card],
                    side=opponent_index,
                    slot_index=len(card_game.table) - 1,
                    is_defense=False,
                    delay=0.0
                )
                card_game.current_turn = card_game.last_attacker = opponent
                card_game.current_defender = card_game.next_player(opponent_index)
                durak_get_defender()
                return

        # Try to find valid defense for all table cards before committing
        reserved_cards = set()
        simulated_defense_queue = []

        for i, (attack_card, (beaten, _)) in enumerate(card_game.table.table.items()):
            if not beaten:
                def_card = opponent.defense(
                    attack_card,
                    card_game.deck.trump_suit,
                    exclude=reserved_cards
                )
                if def_card:
                    simulated_defense_queue.append((i, attack_card, def_card))
                    reserved_cards.add(def_card)
                else:
                    # If AI can't defend one card, stop and force take
                    print("AI cannot fully defend. Must take all cards.")
                    durak_get_next_attacker()
                    return

        # All cards can be defended
        durak_defense_queue = simulated_defense_queue
        durak_defense_index = 0
        confirm_turn = [False, False]
        durak_opponent_do_defense()

    def durak_opponent_do_defense():
        """Executes one defense step at a time using animation + show_anim."""
        global durak_defense_queue, durak_defense_index, confirm_turn

        if durak_defense_index >= len(durak_defense_queue):
            # Done with all defenses
            if card_game.table.beaten():
                print("AI defended all attacks.")
                confirm_turn = [False, False]
            else:
                print("AI failed to defend completely.")
            durak_get_next_attacker()
            return

        slot_index, atk_card, def_card = durak_defense_queue[durak_defense_index]

        play_card_anim(
            cards=[def_card],
            side=card_game.get_player_index(card_game.current_defender),
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

        opponent = card_game.current_defender

        slot_index, atk_card, def_card = durak_defense_queue[durak_defense_index]

        print("Opponent defends", atk_card, "with", def_card)
        card_game.table.beat(atk_card, def_card)
        if def_card in opponent.hand:
            opponent.hand.remove(def_card)
        compute_hand_layout()

        # Next step
        durak_defense_index += 1
        durak_opponent_do_defense()

    # --------------------
    # End Turn Logic
    # --------------------
    def durak_end_turn():
        global confirm_take, confirm_turn

        print("Table before ending turn:", card_game.table)
        print("Player hand before ending turn:", card_game.player.hand)
        for i in range(1, len(card_game.players)):
            print("Opponent {} hand before ending turn:{}", i, card_game.players[i].hand)

        # Lost to two sixes check
        if card_game.current_turn != card_game.player and card_game.deck.is_empty():
            lost_to_two_sixes = card_game.check_for_loss_to_two_sixes()
            if lost_to_two_sixes:
                print("You lost to two sixes in the last round!")

        for i in range(1, len(card_game.players)):
            card_game.players[i].remember_table(card_game.table)
            card_game.players[i].remember_discard(card_game.deck.discard)

        # Animate and resolve the table
        durak_animate_and_resolve_table()

        # Check for game over conditions
        card_game.check_endgame()

        # Check if game has ended
        if card_game.result:
            card_game.state = "result"
            return

        print("Player hand after drawing:", card_game.player.hand)
        for i in range(1, len(card_game.players)):
            print("Opponent {} hand after drawing:{}", i, card_game.players[i].hand)

        confirm_take = False
        confirm_turn = [False, False]

    # --------------------
    # Animation Callbacks
    # --------------------
    def resolve_on_finish(key):
        if key == "durak_player_draw":
            durak_player_draw()
        elif key == "durak_opponent_draw":
            durak_opponent_draw()
        elif key == "durak_opponent_2_draw":
            durak_opponent_2_draw()
        elif key == "durak_opponent_3_draw":
            durak_opponent_3_draw()
        elif key == "durak_resolve_table_logic":
            durak_resolve_table_logic()
        elif key == "durak_opponent_after_turn":
            durak_opponent_after_turn()
        elif key == "durak_player_switch_to_defend":
            durak_player_switch_to_defend()
        elif key == "durak_opponent_apply_defense":
            durak_opponent_apply_defense()