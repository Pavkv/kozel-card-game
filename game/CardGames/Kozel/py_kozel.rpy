init python:
    DISCARD_PLAYERS_X = 50
    PLAYER_DISCARD_Y = 800
    OPPONENT_DISCARD_Y = 0
    # --------------------
    # Kozel Animations
    # --------------------
    def kozel_player_draw():
        draw_anim(side=0, sort_hand=True, on_finish="kozel_end_game_cleanup" if (
            card_game.state not in ["player_defend", "player_drop", "opponent_defend", "opponent_drop"]
            and card_game.deck.is_empty()
            and (
                (not card_game.player.hand and card_game.opponent.hand) or
                (not card_game.opponent.hand and card_game.player.hand)
            )
        ) else None)

    def kozel_opponent_draw():
        draw_anim(side=1, sort_hand=True, on_finish="kozel_end_game_cleanup" if (
            card_game.state not in ["player_defend", "player_drop", "opponent_defend", "opponent_drop"]
            and card_game.deck.is_empty()
            and (
                (not card_game.player.hand and card_game.opponent.hand) or
                (not card_game.opponent.hand and card_game.player.hand)
            )
        ) else None)

    def kozel_resolve_table_logic(receiver):
        """
        Final game logic after table is cleared: handle take/discard, redraw hands, etc.
        """
        card_game.take_cards(receiver)
        card_game.table.clear()

        # Tally points before next turn
        card_game.count_total_points_kozel_both()

        print("Discard pile player:", card_game.player.discard)
        print("Player hand after turn:", card_game.player.hand)
        print("Player points after turn:", card_game.player_points)
        print("Discard pile opponent:", card_game.opponent.discard)
        print("Opponent hand after turn:", card_game.opponent.hand)
        print("Opponent points after turn:", card_game.opponent_points)

        # Switch state to next turn
        card_game.state = (
            "player_turn" if card_game.current_turn == card_game.player else "opponent_turn"
        )

        # Draw cards (opposite side first)
        if card_game.current_turn == card_game.player:
            draw_anim(side=0, sort_hand=True, on_finish="kozel_opponent_draw")
        else:
            draw_anim(side=1, sort_hand=True, on_finish="kozel_player_draw")

        # Sort and re-render
        card_game.player.sort_hand(card_game.deck.trump_suit)
        card_game.opponent.sort_hand(card_game.deck.trump_suit)
        compute_hand_layout()

    def kozel_animate_and_resolve_table(step_delay=0.05, anim_duration=0.1):
        """
        Animate clearing the table and then resolve the logic based on whether the cards
        were defended (discarded) or taken.
        """
        global hovered_card_index, confirm_drop

        table_animations[:] = []
        delay = 0.0

        # Determine who receives the cards
        if confirm_drop:
            receiver = card_game.current_turn  # Attacker takes cards
        else:
            receiver = card_game.player if card_game.current_turn == card_game.opponent else card_game.opponent
            card_game.current_turn = card_game.opponent if card_game.current_turn == card_game.player else card_game.player

        print("Animating table resolution. Receiver:", receiver.name)

        # Animate each card from the table
        for i, (atk_card, (beaten, def_card)) in enumerate(card_game.table.table.items()):
            src_x = 350 + i * 200
            src_y = 375
            cards = list(filter(None, [atk_card, def_card]))

            for card in cards:
                anim = {
                    "card": card,
                    "src_x": src_x,
                    "src_y": src_y if card == atk_card else src_y + 120,
                    "delay": delay,
                    "duration": anim_duration,
                }

                dest_y = PLAYER_DISCARD_Y if receiver == card_game.player else OPPONENT_DISCARD_Y
                anim.update({
                    "dest_x": DISCARD_PLAYERS_X,
                    "dest_y": dest_y,
                    "target": "discard",
                })

                table_animations.append(anim)
                delay += step_delay

        # Show animation, pass `receiver` as tuple to args
        show_anim(
            on_finish="kozel_resolve_table_logic",
            args=(receiver,)
        )

        # Reset selection
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

            confirm_drop = len(selected_attack_card_indexes) == card_game.table.num_unbeaten()
            if not confirm_drop:
                print("Player cannot defend against:", selected_attack_card)
                print("Player has to drop same number of cards as attacks.")

    def kozel_player_switch_to_defend():
        global confirm_attack, selected_attack_card_indexes
        selected_attack_card_indexes.clear()
        confirm_attack = False
        card_game.state = "opponent_defend"

    def kozel_confirm_selected_attack():
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
                    on_finish="kozel_player_switch_to_defend"
                )

            else:
                print("Invalid attack. Resetting selection.")
                selected_attack_card_indexes.clear()
                confirm_attack = False

    def kozel_player_drop():
        """Handles player dropping cards logic, one at a time with animation callbacks."""
        global selected_attack_card_indexes, kozel_drop_queue, kozel_drop_index

        indexes = sorted(selected_attack_card_indexes)
        cards = [card_game.player.hand[i] for i in indexes]

        if len(cards) != card_game.table.num_unbeaten():
            print("Invalid drop: must match table count.")
            return

        print("Player drops cards:", cards)
        kozel_drop_queue = []
        kozel_drop_index = 0

        card_index = 0
        for i, (attack_card, (beaten, _)) in enumerate(card_game.table.table.items()):
            if beaten:
                continue
            def_card = cards[card_index]
            kozel_drop_queue.append((i, attack_card, def_card))
            card_index += 1

        selected_attack_card_indexes.clear()

        # Start first drop
        kozel_player_do_drop()

    def kozel_player_do_drop():
        """Handles one drop animation at a time."""
        global kozel_drop_queue, kozel_drop_index

        if kozel_drop_index >= len(kozel_drop_queue):
            print("Player finished dropping cards.")
            card_game.state = "end_turn"
            compute_hand_layout()
            return

        slot_index, atk_card, def_card = kozel_drop_queue[kozel_drop_index]
        print("Animating drop: {} on {}".format(def_card, atk_card))

        play_card_anim(
            cards=[def_card],
            side=0,
            slot_index=slot_index,
            is_defense=True,
            skip_check=True
        )

        # Wait for animation, then continue logic
        show_anim(on_finish="kozel_player_apply_drop")

    def kozel_player_apply_drop():
        """Applies the dropped card and continues to the next."""
        global selected_attack_card_indexes, kozel_drop_queue, kozel_drop_index

        slot_index, atk_card, def_card = kozel_drop_queue[kozel_drop_index]

        print("Applying drop: {} -> {}".format(def_card, atk_card))
        card_game.table.beat(atk_card, def_card)

        if def_card in card_game.player.hand:
            card_game.player.hand.remove(def_card)

        compute_hand_layout()

        kozel_drop_index += 1
        kozel_player_do_drop()

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
        global confirm_drop, kozel_defense_queue, kozel_defense_index

        reserved_cards = set()
        kozel_defense_queue = []
        kozel_defense_index = 0

        for i, (attack_card, (beaten, _)) in enumerate(card_game.table.table.items()):
            if not beaten:
                def_card = card_game.opponent.defense(
                    attack_card,
                    card_game.deck.trump_suit,
                    exclude=reserved_cards
                )
                if def_card:
                    kozel_defense_queue.append((i, attack_card, def_card))
                    reserved_cards.add(def_card)
                else:
                    print("AI cannot defend against:", attack_card)
                    confirm_drop = True
                    card_game.state = "opponent_drop"
                    kozel_opponent_drop()
                    return

        print("AI defense queue:", kozel_defense_queue)

        if kozel_defense_queue:
            kozel_opponent_do_defense()
        else:
            print("AI could not defend. Switching to drop.")
            confirm_drop = True
            card_game.state = "opponent_drop"
            kozel_opponent_drop()

    def kozel_opponent_do_defense():
        """Animates one card defense at a time."""
        global kozel_defense_index, kozel_defense_queue

        if kozel_defense_index >= len(kozel_defense_queue):
            if card_game.table.beaten():
                print("AI successfully defended all attacks.")
                card_game.state = "end_turn"
            else:
                print("AI failed to defend all. Switching to drop.")
                confirm_drop = True
                card_game.state = "opponent_drop"
                kozel_opponent_drop()
            return

        slot_index, atk_card, def_card = kozel_defense_queue[kozel_defense_index]
        print("AI defends {} with {}".format(atk_card, def_card))

        play_card_anim(
            cards=[def_card],
            side=1,
            slot_index=slot_index,
            is_defense=True,
            delay=0.0
        )

        show_anim(on_finish="kozel_opponent_apply_defense")

    def kozel_opponent_apply_defense():
        """Applies the defense and proceeds to next."""
        global kozel_defense_index, kozel_defense_queue

        slot_index, atk_card, def_card = kozel_defense_queue[kozel_defense_index]

        card_game.table.beat(atk_card, def_card)
        if def_card in card_game.opponent.hand:
            card_game.opponent.hand.remove(def_card)

        compute_hand_layout()
        kozel_defense_index += 1
        kozel_opponent_do_defense()

    def kozel_opponent_drop():
        """Handles opponent dropping cards logic with animation."""
        global kozel_drop_queue, kozel_drop_index

        kozel_drop_index = 0
        kozel_drop_queue = []

        opponent_drop = card_game.opponent.drop_cards(card_game.table.keys())
        print("AI drops cards:", opponent_drop)

        for i, (attack_card, (beaten, _)) in enumerate(card_game.table.table.items()):
            def_card = opponent_drop[i]
            kozel_drop_queue.append((i, attack_card, def_card))

        if kozel_drop_queue:
            kozel_opponent_do_drop()
        else:
            print("Nothing to drop.")
            card_game.state = "end_turn"

    def kozel_opponent_do_drop():
        """Performs a single card drop with animation."""
        global kozel_drop_index, kozel_drop_queue

        if card_game.table.beaten():
            print("AI dropped all cards.")
            card_game.state = "end_turn"
            return

        if kozel_drop_index >= len(kozel_drop_queue):
            print("AI drop queue finished.")
            card_game.state = "end_turn"
            return

        slot_index, atk_card, def_card = kozel_drop_queue[kozel_drop_index]
        print("AI drops {} to beat {}".format(def_card, atk_card))

        play_card_anim(
            cards=[def_card],
            side=1,
            slot_index=slot_index,
            is_defense=True,
            skip_check=True
        )

        show_anim(on_finish="kozel_opponent_apply_drop")

    def kozel_opponent_apply_drop():
        """Applies drop logic after animation step."""
        global kozel_drop_index, kozel_drop_queue

        slot_index, atk_card, def_card = kozel_drop_queue[kozel_drop_index]

        card_game.table.beat(atk_card, def_card)
        if def_card in card_game.opponent.hand:
            card_game.opponent.hand.remove(def_card)

        compute_hand_layout()

        kozel_drop_index += 1
        kozel_opponent_do_drop()

    # --------------------
    # End Turn Logic
    # --------------------
    def kozel_end_turn():
        """Handles end turn logic: remembering cards, animating table resolution, checking endgame."""

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

    # --------------------
    # End Game Cleanup
    # --------------------
    def kozel_apply_discard(player, cards, on_finish=None):
        for card in cards:
            player.discard.append(card)
            if card in player.hand:
                player.hand.remove(card)

        compute_hand_layout()

        if isinstance(on_finish, str):
            resolve_on_finish(on_finish)

    def kozel_end_game_cleanup():
        """Handles cleanup when one player runs out of cards and the deck is empty."""

        if (
            card_game.state not in ["player_defend", "player_drop", "opponent_defend", "opponent_drop"]
            and card_game.deck.is_empty()
            and (
                (not card_game.player.hand and card_game.opponent.hand) or
                (not card_game.opponent.hand and card_game.player.hand)
            )
        ):
            if not card_game.player.hand and card_game.opponent.hand:
                print("Player is out of cards. Opponent discards remaining hand.")
                player = card_game.opponent
            elif not card_game.opponent.hand and card_game.player.hand:
                print("Opponent is out of cards. Player discards remaining hand.")
                player = card_game.player
            else:
                return

            cards = [card for card in player.hand if card is not None]

            print("{} discarding: " + ', '.join(str(c) for c in cards).format(player.name))

            card_game.state = "game_cleanup"
            table_animations[:] = []

            side = 0 if player == card_game.player else 1
            delay = 0.0
            anim_duration = 0.3

            for i, card in enumerate(cards):
                src_x, src_y = hand_card_pos(side, card)

                override_img = get_card_image(card) if side == 0 else base_cover_img_src

                table_animations.append({
                    "card": card,
                    "src_x": src_x,
                    "src_y": src_y,
                    "dest_x": DISCARD_PLAYERS_X,
                    "dest_y": PLAYER_DISCARD_Y if side == 0 else OPPONENT_DISCARD_Y,
                    "delay": delay + i * 0.2,
                    "duration": anim_duration,
                    "override_img": override_img,
                })

            show_anim(
                on_finish="kozel_apply_discard",
                args=(player, cards),
                kwargs={"on_finish": "kozel_end_turn"}
            )

    # --------------------
    # Animation Callbacks
    # --------------------
    def resolve_on_finish(key):
        if key == "kozel_player_switch_to_defend":
            kozel_player_switch_to_defend()
        elif key == "kozel_player_apply_drop":
            kozel_player_apply_drop()
        elif key == "kozel_opponent_apply_defense":
            kozel_opponent_apply_defense()
        elif key == "kozel_opponent_apply_drop":
            kozel_opponent_apply_drop()
        elif key == "kozel_resolve_table_logic":
            kozel_resolve_table_logic()
        elif key == "kozel_player_draw":
            kozel_player_draw()
        elif key == "kozel_opponent_draw":
            kozel_opponent_draw()
        elif key == "kozel_end_turn":
            kozel_end_turn()
        elif key == "kozel_apply_discard":
            kozel_apply_discard()
        elif key == "kozel_end_game_cleanup":
            kozel_end_game_cleanup()

