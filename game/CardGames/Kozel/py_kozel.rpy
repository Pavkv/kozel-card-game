init python:
    # --------------------
    # Support Functions
    # --------------------
    def kozel_get_next_defender():
        """Get the next defender in the circle."""
        global confirm_drop

        if not confirm_drop:
            card_game.last_attacker = card_game.current_turn

        kozel_discard_beaten_cards()

    def kozel_discard_beaten_cards():
        """Animate and discard beaten cards if applicable."""
        if (
            isinstance(card_game, KozelGame)
            and card_game.number_of_opponents > 1
            and not card_game.is_player_last()
            and card_game.state not in ["player_turn", "opponent_turn"]
            and card_game.table.beaten()
        ):
            print("[Kozel] Animating discard of beaten/drop cards.")
            kozel_animate_discard(confirm_drop)
        else:
            kozel_apply_discard(False)

    def kozel_apply_discard(is_drop):
        """After animation, move cards into discard pile."""
        global selected_attack_card, confirm_drop

        selected_attack_card = None
        confirm_drop = False

        if card_game.is_player_last():
            print("Last attacker's turn. Ending turn.")
            card_game.state = "end_turn"
            return

        if card_game.table.beaten():
            card_game.table.discard_beaten(card_game.deck.discard, is_drop)
            print("Discard pile:", card_game.deck.discard)

        current_player_index = card_game.get_player_index(card_game.current_turn)

        print("Switching to next player's turn.")
        next_player = card_game.next_player(current_player_index)
        card_game.current_turn = next_player
        card_game.state = "opponent_defend" if next_player != card_game.player else "player_defend"

    # --------------------
    # Kozel Animations
    # --------------------
    def kozel_count_points():
        card_game.check_endgame()

        # Check if game has ended
        if card_game.result:
            card_game.state = "result"
            print("Player points:", card_game.players_points[0])
            for i in range(1, len(card_game.players)):
                print("Opponent {} hand after drawing:{}", i, card_game.players_points[1])
            print("Game over with result:", card_game.result)
            return

        for point in card_game.players_points:
            print("Player points after turn:", point)

        print("Player hand after drawing:", card_game.player.hand)
        for i in range(1, len(card_game.players)):
            print("Opponent {} hand after drawing:{}", i, card_game.players[i].hand)

    def kozel_player_draw():
        global draw_up_to_hand_size
        next_side = get_next_draw_side()
        if next_side is None:
            on_finish = "kozel_count_points"
        else:
            on_finish = next_side
        draw_anim(side=0, target_count=draw_up_to_hand_size, sort_hand=True, on_finish=on_finish)

    def kozel_opponent_draw():
        global draw_up_to_hand_size
        next_side = get_next_draw_side()
        if next_side is None:
            on_finish = "kozel_count_points"
        else:
            on_finish = next_side
        draw_anim(side=1, target_count=draw_up_to_hand_size, sort_hand=True, on_finish=on_finish)

    def kozel_opponent_2_draw():
        global draw_up_to_hand_size
        next_side = get_next_draw_side()
        if next_side is None:
            on_finish = "kozel_count_points"
        else:
            on_finish = next_side
        draw_anim(side=2, target_count=draw_up_to_hand_size, sort_hand=True, on_finish=on_finish)

    def kozel_opponent_3_draw():
        global draw_up_to_hand_size
        next_side = get_next_draw_side()
        if next_side is None:
            on_finish = "kozel_count_points"
        else:
            on_finish = next_side
        draw_anim(side=3, target_count=draw_up_to_hand_size, sort_hand=True, on_finish=on_finish)

    def kozel_resolve_table_logic(receiver, receiver_index):
        """
        Final game logic after table is cleared: handle take/discard, redraw hands, etc.
        """
        global on_finish_draw_animations, draw_up_to_hand_size

        card_game.take_cards(receiver)
        card_game.table.clear()
        card_game.count_total_points()

        # Switch to next turn
        card_game.state = (
            "player_turn" if card_game.current_turn == card_game.player else "opponent_turn"
        )

        first_to_draw = receiver_index
        cards_left_in_deck = len(card_game.deck.cards)
        previous_player = card_game.previous_player(receiver_index)
        draw_up_to_hand_size = cards_left_in_deck // len(card_game.players) + len(card_game.player.hand)

        while (
            (cards_left_in_deck > len(card_game.players) - 1 and len(card_game.deck.cards) > len(card_game.players)) or
            (cards_left_in_deck > 0 and len(card_game.deck.cards) == len(card_game.players)) or
            (len(previous_player.hand) < 6 and cards_left_in_deck > 0)
        ):
            p = card_game.players[first_to_draw % len(card_game.players)]
            on_finish_draw_animations.append(kozel_draw_animations_dict[card_game.get_player_index(p)])
            first_to_draw += 1
            cards_left_in_deck -= 1

        draw_up_to_hand_size = min(draw_up_to_hand_size, 6)

        if on_finish_draw_animations:
            resolve_on_finish(on_finish_draw_animations.pop(0))
        else:
            kozel_count_points()

    def kozel_animate_and_resolve_table(step_delay=0.05, anim_duration=0.1):
        """
        Animate all table cards and discard pile cards moving to a player, then resolve.
        """
        global hovered_card_index, confirm_drop

        table_animations[:] = []
        delay = 0.0

        receiver = card_game.last_attacker
        receiver_index = card_game.get_player_index(receiver)
        card_game.current_turn = receiver

        print("Receiver of table cards:", receiver.name)

        X_HANDS = {
            1: [KOZEL_PLAYERS_X, OPPONENT_HAND_X],
            2: [KOZEL_PLAYERS_X, OPPONENT_HAND_X, OPPONENT_2_HAND_X],
            3: [KOZEL_PLAYERS_X, OPPONENT_3_HAND_X, OPPONENT_HAND_X, OPPONENT_2_HAND_X],
        }

        dest_x = (
            X_HANDS[card_game.number_of_opponents][receiver_index] + 20
            if card_game.number_of_opponents > 1 else KOZEL_PLAYERS_X
        )
        dest_y = KOZEL_PLAYER_DISCARD_Y if receiver == card_game.player else KOZEL_OPPONENT_DISCARD_Y

        # Animate table cards (attack and defense)
        pair_count = len(card_game.table.table)
        max_table_width = 1280
        card_width = CARD_WIDTH
        spacing = min(200, (max_table_width - pair_count * card_width) // max(1, pair_count - 1)) if pair_count > 1 else 0
        total_width = pair_count * card_width + (pair_count - 1) * spacing if pair_count > 1 else card_width
        start_x = (config.screen_width - max_table_width) // 2 + (max_table_width - total_width) // 2

        for i, (atk_card, (_, def_card)) in enumerate(card_game.table.table.items()):
            src_x = start_x + i * (card_width + spacing)

            for card, offset_y in [(atk_card, 0), (def_card, 120)]:
                if card:
                    table_animations.append({
                        "card": card,
                        "src_x": src_x,
                        "src_y": 375 + offset_y,
                        "dest_x": dest_x,
                        "dest_y": dest_y,
                        "delay": delay,
                        "duration": anim_duration,
                    })

            delay += step_delay

        # Animate any existing discard pile cards (if visualized)
        for card in card_game.deck.discard:
            table_animations.append({
                "card": card,
                "src_x": DISCARD_X,
                "src_y": DISCARD_Y,
                "dest_x": dest_x,
                "dest_y": dest_y,
                "delay": delay,
                "duration": anim_duration,
                "override_img": base_cover_img_src,
            })
            delay += step_delay

        show_anim(
            on_finish="kozel_resolve_table_logic",
            args=(receiver, receiver_index),
        )

        hovered_card_index = -1
        card_game.initial_attacker_index = receiver_index

    def kozel_animate_discard(is_drop):
        """Create animations for discarding beaten or dropped cards."""
        from_pos = {}
        table_animations[:] = []

        anim_duration = 0.15
        delay = 0.0

        for atk_card, (beaten, def_card) in card_game.table.table.items():
            card = def_card if is_drop else atk_card
            from_pos[card] = table_card_pos(card)
            table_animations.append({
                "card": card,
                "src_x": from_pos[card][0],
                "src_y": from_pos[card][1],
                "dest_x": DISCARD_X,
                "dest_y": DISCARD_Y,
                "delay": delay,
                "duration": anim_duration,
                "override_img": base_cover_img_src,
            })

        show_anim(
            on_finish="kozel_apply_discard",
            args=(is_drop,),
        )

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
        card_game.last_attacker = card_game.player
        kozel_get_next_defender()

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
        global selected_attack_card_indexes, drop_queue, drop_index

        indexes = sorted(selected_attack_card_indexes)
        cards = [card_game.player.hand[i] for i in indexes]

        if len(cards) != card_game.table.num_unbeaten():
            print("Invalid drop: must match table count.")
            return

        print("Player drops cards:", cards)
        drop_queue = []
        drop_index = 0

        card_index = 0
        for i, (attack_card, (beaten, _)) in enumerate(card_game.table.table.items()):
            if beaten:
                continue
            def_card = cards[card_index]
            drop_queue.append((i, attack_card, def_card))
            card_index += 1

        selected_attack_card_indexes.clear()

        # Start first drop
        kozel_player_do_drop()

    def kozel_player_do_drop():
        """Handles one drop animation at a time."""
        global drop_queue, drop_index

        if drop_index >= len(drop_queue):
            print("Player finished dropping cards.")
            kozel_get_next_defender()
            return

        slot_index, atk_card, def_card = drop_queue[drop_index]
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
        global selected_attack_card_indexes, drop_queue, drop_index

        slot_index, atk_card, def_card = drop_queue[drop_index]

        print("Applying drop: {} -> {}".format(def_card, atk_card))
        card_game.table.beat(atk_card, def_card)

        if def_card in card_game.player.hand:
            card_game.player.hand.remove(def_card)

        compute_hand_layout()

        drop_index += 1
        kozel_player_do_drop()

    # --------------------
    # Opponent Functions
    # --------------------
    def kozel_opponent_turn():
        """Handles opponent's attack selection logic."""
        opponent_index = card_game.get_player_index(card_game.current_turn)

        cards = card_game.opponent_attack()
        print("AI attacked successfully with:", cards)

        start_index = len(card_game.table)
        play_card_anim(
            cards=cards,
            side=opponent_index,
            slot_index=start_index,
            is_defense=False,
        )

        kozel_get_next_defender()

    def kozel_opponent_defend():
        """Handles the opponent's defense logic sequentially with animation."""
        global confirm_drop, kozel_defense_queue, kozel_defense_index

        opponent = card_game.current_turn
        opponent_index = card_game.get_player_index(opponent)

        reserved_cards = set()
        kozel_defense_queue = []
        kozel_defense_index = 0

        for i, (attack_card, (beaten, _)) in enumerate(card_game.table.table.items()):
            if not beaten:
                def_card = opponent.defense(
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

        opponent = card_game.current_turn
        opponent_index = card_game.get_player_index(opponent)

        if kozel_defense_index >= len(kozel_defense_queue):
            if card_game.table.beaten():
                print("AI successfully defended all attacks.")
                kozel_get_next_defender()
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
            side=opponent_index,
            slot_index=slot_index,
            is_defense=True,
        )

        show_anim(on_finish="kozel_opponent_apply_defense")

    def kozel_opponent_apply_defense():
        """Applies the defense and proceeds to next."""
        global kozel_defense_index, kozel_defense_queue

        opponent = card_game.current_turn

        slot_index, atk_card, def_card = kozel_defense_queue[kozel_defense_index]

        card_game.table.beat(atk_card, def_card)
        if def_card in opponent.hand:
            opponent.hand.remove(def_card)

        compute_hand_layout()
        kozel_defense_index += 1
        kozel_opponent_do_defense()

    def kozel_opponent_drop():
        """Handles opponent dropping cards logic with animation."""
        global drop_queue, drop_index

        opponent = card_game.current_turn

        drop_index = 0
        drop_queue = []

        opponent_drop = opponent.drop_cards(card_game.table.keys())
        print("AI drops cards:", opponent_drop)

        for i, (attack_card, (beaten, _)) in enumerate(card_game.table.table.items()):
            def_card = opponent_drop[i]
            drop_queue.append((i, attack_card, def_card))

        if drop_queue:
            kozel_opponent_do_drop()
        else:
            print("Nothing to drop.")
            kozel_get_next_defender()

    def kozel_opponent_do_drop():
        """Performs a single card drop with animation."""
        global drop_index, drop_queue

        opponent = card_game.current_turn
        opponent_index = card_game.get_player_index(opponent)

        if card_game.table.beaten():
            print("AI dropped all cards.")
            kozel_get_next_defender()
            return

        if drop_index >= len(drop_queue):
            print("AI drop queue finished.")
            kozel_get_next_defender()
            return

        slot_index, atk_card, def_card = drop_queue[drop_index]
        print("AI drops {} to beat {}".format(def_card, atk_card))

        play_card_anim(
            cards=[def_card],
            side=opponent_index,
            slot_index=slot_index,
            is_defense=True,
            skip_check=True
        )

        show_anim(on_finish="kozel_opponent_apply_drop")

    def kozel_opponent_apply_drop():
        """Applies drop logic after animation step."""
        global drop_index, drop_queue

        opponent = card_game.current_turn

        slot_index, atk_card, def_card = drop_queue[drop_index]

        card_game.table.beat(atk_card, def_card)
        opponent.hand.remove(def_card)

        compute_hand_layout()

        drop_index += 1
        kozel_opponent_do_drop()

    # --------------------
    # End Turn Logic
    # --------------------
    def kozel_end_turn():
        """Handles end turn logic: remembering cards, animating table resolution, checking endgame."""

        print("Table before ending turn:", card_game.table)
        print("Player hand before ending turn:", card_game.player.hand)
        for i in range(1, len(card_game.players)):
            print("Opponent {} hand before ending turn:{}", i, card_game.players[i].hand)

        for i in range(1, len(card_game.players)):
            card_game.players[i].remember_table(card_game.table)
            card_game.players[i].remember_discard(card_game.deck.discard)

        # Animate and resolve the table
        kozel_animate_and_resolve_table()

    # --------------------
    # Animation Callbacks
    # --------------------
    def resolve_on_finish(key):
        if key == "kozel_player_switch_to_defend":
            kozel_player_switch_to_defend()
        elif key == "kozel_discard_beaten_cards":
            kozel_discard_beaten_cards()
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
        elif key == "kozel_apply_discard":
            kozel_apply_discard()
        elif key == "kozel_opponent_draw":
            kozel_opponent_draw()
        elif key == "kozel_opponent_2_draw":
            kozel_opponent_2_draw()
        elif key == "kozel_opponent_3_draw":
            kozel_opponent_3_draw()
        elif key == "kozel_count_points":
            kozel_count_points()
        elif key == "kozel_end_turn":
            kozel_end_turn()

