init python:
    DISCARD_X = 50
    PLAYER_DISCARD_Y = 800
    OPPONENT_DISCARD_Y = 0
     # --------------------
     # Durak Animations
     # --------------------
    def kozel_animate_and_resolve_table(step_delay=0.05, anim_duration=0.1):
        global hovered_card_index, confirm_drop
        """
        Animate cards being cleared from the table and defer logic until after animation.
        """

        table_animations[:] = []
        delay = 0.0

        is_beaten = card_game.table.beaten()

        if confirm_drop:
            receiver = card_game.current_turn
        else:
            receiver = card_game.player if card_game.current_turn == card_game.opponent else card_game.opponent  # The defender takes the cards
            card_game.current_turn = card_game.opponent if card_game.current_turn == card_game.player else card_game.player

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
                
                dest_y_beaten = PLAYER_DISCARD_Y if receiver == card_game.player else OPPONENT_DISCARD_Y
                dest_y_not_beaten = OPPONENT_DISCARD_Y if receiver == card_game.player else PLAYER_DISCARD_Y
                if not confirm_drop:
                    anim.update({
                        "dest_x": DISCARD_X,
                        "dest_y": dest_y_beaten,
                        "target": "discard",
                    })
                else:
                    anim.update({
                        "dest_x": DISCARD_X,
                        "dest_y": dest_y_not_beaten,
                        "target": "discard",
                    })

                table_animations.append(anim)
                delay += step_delay

        def resolve_table_logic():
            card_game.take_cards(receiver)
            card_game.state = (
                "player_turn" if card_game.current_turn == card_game.player else "opponent_turn"
            )

            card_game.count_total_points_kozel_both()
            card_game.table.clear()

            print("Discard pile player:", card_game.player.discard)
            print("Player hand after turn:", card_game.player.hand)
            print("Player points after turn:", card_game.player_points)
            print("Discard pile opponent:", card_game.opponent.discard)
            print("Opponent hand after turn:", card_game.opponent.hand)
            print("Opponent points after turn:", card_game.opponent_points)

            if card_game.current_turn == card_game.opponent:
                draw_anim(side=0, sort_hand=True, on_finish=lambda: draw_anim(side=1, sort_hand=True))
            else:
                draw_anim(side=1, sort_hand=True, on_finish=lambda: draw_anim(side=0, sort_hand=True))

            card_game.player.sort_hand(card_game.deck.trump_suit)
            card_game.opponent.sort_hand(card_game.deck.trump_suit)

            compute_hand_layout()

        show_anim(function=resolve_table_logic)

        hovered_card_index = -1
        confirm_drop = False

    # --------------------
    # Player Functions
    # --------------------
    def kozel_handle_card_click(index):
        """Handles card click events for player actions."""
        global confirm_attack, confirm_drop, selected_attack_card_indexes, selected_attack_card

        card = card_game.player.hand[index]
        print("Card clicked:", card)

        # Player attack phase
        if card_game.state == "player_turn":
            if index in selected_attack_card_indexes:
                selected_attack_card_indexes.remove(index)
                print("Unselected:", card)
            else:
                # Allow selecting if first or same rank as already selected
                allowed_suits = {card_game.player.hand[i].suit for i in selected_attack_card_indexes}
                if not selected_attack_card_indexes or card.suit in allowed_suits:
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
            else:
                print("Invalid defense with:", card)
                selected_attack_card = None

        if card_game.table.beaten():
            print("All attacks beaten. Player wins this round.")
            card_game.state = "end_turn"
            selected_attack_card = None

        elif not card_game.table.beaten() and card_game.state == "player_drop":
            if index in selected_attack_card_indexes:
                selected_attack_card_indexes.remove(index)
                print("Unselected:", card)
            else:
                selected_attack_card_indexes.add(index)
                print("Selected:", card)

            confirm_drop = len(selected_attack_card_indexes) == len(card_game.table.keys())
            if not confirm_drop:
                print("Player cannot defend against:", selected_attack_card)
                print("Player has to drop same number of cards as attacks.")

    def kozel_confirm_selected_attack():
        """Confirms all selected attack cards and animates them from hand to table."""
        global confirm_attack, selected_attack_card_indexes

        if confirm_attack and selected_attack_card_indexes:
            indexes = sorted(selected_attack_card_indexes)
            cards = [card_game.player.hand[i] for i in indexes]

            if card_game.can_attack(card_game.player):
                print("Player attacked with: " + ', '.join(str(c) for c in cards))

                def switch_to_defend():
                    selected_attack_card_indexes.clear()
                    confirm_attack = False
                    card_game.state = "opponent_defend"

                # Animate each card moving to table
                start_index = len(card_game.table)
                play_card_anim(
                    cards=cards,
                    side=0,
                    slot_index=start_index,
                    is_defense=False,
                    on_finish=switch_to_defend
                )

            else:
                print("Invalid attack. Resetting selection.")
                selected_attack_card_indexes.clear()
                confirm_attack = False

    def kozel_player_drop():
        """Handles player dropping cards logic."""
        global selected_attack_card_indexes

        indexes = sorted(selected_attack_card_indexes)
        cards = [card_game.player.hand[i] for i in indexes]

        print(cards)

        if len(cards) == len(card_game.table.keys()):
            print("Player drops cards:", cards)

            cards_to_drop = []

            for i, (attack_card, (beaten, _)) in enumerate(card_game.table.table.items()):
                def_card = cards[i]
                cards_to_drop.append((i, attack_card, def_card))

            def do_drop(index=0):
                if card_game.table.beaten():
                    print("AI dropped all cards.")
                    card_game.state = "end_turn"
                    return

                slot_index, atk_card, def_card = cards_to_drop[index]

                def apply_drop():
                    # Now it's safe to update the game state
                    card_game.table.beat(atk_card, def_card)
                    card_game.player.hand.remove(def_card)
                    compute_hand_layout()

                    # Move to next defense
                    do_drop(index + 1)

                # Animate it
                play_card_anim(
                    cards=[def_card],
                    side=0,
                    slot_index=slot_index,
                    is_defense=True,
                    skip_check=True
                )
                show_anim(apply_drop)

            do_drop()

            # Clear selection and proceed to opponent turn
            selected_attack_card_indexes.clear()
            card_game.state = "end_turn"

    # --------------------
    # Opponent Functions
    # --------------------
    def kozel_opponent_turn():
        """Handles opponent's attack selection logic."""
        if card_game.can_attack(card_game.opponent):
            cards = card_game.opponent_attack()[1]
            print("AI attacked successfully with:", cards)

            start_index = len(card_game.table)
            play_card_anim(
                cards=cards,
                side=1,
                slot_index=start_index,
                is_defense=False,
            )

            card_game.state = "player_defend"

    def kozel_opponent_defend():
        """Handles the opponent's defense logic sequentially with animation."""
        global confirm_drop
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
                    confirm_drop = True
                    card_game.state = "opponent_drop"
                    kozel_opponent_drop()
                    return

        print("AI defense queue:", defense_queue)

        def do_defense(index=0):
            if index >= len(defense_queue):
                # All done — now check if fully defended
                if card_game.table.beaten():
                    print("AI defended all attacks.")
                    card_game.state = "end_turn"
                    return
                else:
                    print("AI failed to defend completely.")
                    confirm_drop = True
                    card_game.state = "opponent_drop"
                    kozel_opponent_drop()

            slot_index, atk_card, def_card = defense_queue[index]

            def apply_defense():
                # Now it's safe to update the game state
                card_game.table.beat(atk_card, def_card)
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
            show_anim(apply_defense)

        if defense_queue:
            do_defense()
        else:
            print("AI could not defend. Player wins this round.")
            confirm_drop = True
            card_game.state = "opponent_drop"
            kozel_opponent_drop()

    def kozel_opponent_drop():
        """Handles opponent dropping cards logic."""
        opponent_drop = card_game.opponent.drop_cards(card_game.table.keys())
        print("AI drops cards:", opponent_drop)

        cards_to_drop = []

        for i, (attack_card, (beaten, _)) in enumerate(card_game.table.table.items()):
            def_card = opponent_drop[i]
            cards_to_drop.append((i, attack_card, def_card))

        def do_drop(index=0):
            if card_game.table.beaten():
                print("AI dropped all cards.")
                card_game.state = "end_turn"
                return

            slot_index, atk_card, def_card = cards_to_drop[index]

            def apply_drop():
                # Now it's safe to update the game state
                card_game.table.beat(atk_card, def_card)
                card_game.opponent.hand.remove(def_card)
                compute_hand_layout()

                # Move to next defense
                do_drop(index + 1)

            # Animate it
            play_card_anim(
                cards=[def_card],
                side=1,
                slot_index=slot_index,
                is_defense=True,
                skip_check=True
            )
            show_anim(apply_drop)

        do_drop()

    # --------------------
    # End Turn Logic
    # --------------------
    def kozel_end_turn():
        print("Table before ending turn:", card_game.table)
        print("Player hand before ending turn:", card_game.player.hand)
        print("Opponent hand before ending turn:", card_game.opponent.hand)

        card_game.opponent.remember_cards(card_game.table.keys())
        card_game.opponent.remember_cards(card_game.table.values())

        # Animate and resolve the table
        kozel_animate_and_resolve_table()

        # Check for game over conditions
        card_game.check_endgame()

        # Check if game has ended
        if card_game.result:
            card_game.state = "result"
            return

        print("Player hand after drawing:", card_game.player.hand)
        print("Opponent hand after drawing:", card_game.opponent.hand)
