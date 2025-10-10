init python:
    def els_swap_cards_anim(side_index, i, j, base_delay=0.5, anim_duration=1.0):
        """Smooth animation: cards slide into each other's position in-place."""

        hand = card_game.player.hand if side_index == 0 else card_game.opponent.hand
        card_i = hand[i]
        card_j = hand[j]

        # Position before swap
        src_i = hand_card_pos(side_index, card_i)
        src_j = hand_card_pos(side_index, card_j)

        # Use appropriate images
        img_i = get_card_image(card_i) if side_index == 0 else base_cover_img_src
        img_j = get_card_image(card_j) if side_index == 0 else base_cover_img_src

        # Prepare animation entries
        table_animations[:] = [
            {
                "card": card_i,
                "src_x": src_i[0], "src_y": src_i[1],
                "dest_x": src_j[0], "dest_y": src_j[1],
                "delay": base_delay,
                "duration": anim_duration,
                "target": "hand" + str(side_index),
                "override_img": img_i,
            },
            {
                "card": card_j,
                "src_x": src_j[0], "src_y": src_j[1],
                "dest_x": src_i[0], "dest_y": src_i[1],
                "delay": base_delay,
                "duration": anim_duration,
                "target": "hand" + str(side_index),
                "override_img": img_j,
            },
        ]

        show_anim()

        # Swap cards in data
        hand[i], hand[j] = hand[j], hand[i]
        compute_hand_layout()

    # ----------------------------
    # User Functions
    # ----------------------------
    def els_swap_cards_player(selected_card_index):
        """Handle player's card swap during defense phase."""
        global selected_exchange_card_index_player, hovered_card_index

        print(card_game.player.hand)

        # Save then clear selection/hover before animating
        index = selected_exchange_card_index_player
        selected_exchange_card_index_player = -1
        hovered_card_index = -1

        els_swap_cards_anim(0, selected_card_index, index)

        selected_exchange_card_index_player = index
        card_game.turn += 1
        card_game.state = "opponent_turn"

        print(card_game.player.hand)
        compute_hand_layout()

    def els_user_take_from_opponent(index):
        """Handle user taking a card from opponent during defense phase."""
        global selected_exchange_card_index_opponent, hovered_card_index_exchange
        take_card_anim(from_side=1, to_side=0, index=selected_exchange_card_index_opponent)
        card_game.turn = 1
        card_game.round += 1
        selected_exchange_card_index_opponent = -1
        hovered_card_index_exchange = -1
        card_game.state = "opponent_turn"
        renpy.jump("els_game_loop")

    # ----------------------------
    # Opponent Functions
    # ----------------------------
    def els_swap_cards_opponent():
        """Handle opponent's card swap during defense phase."""
        global selected_exchange_card_index_opponent, hovered_card_index_exchange

        card_game.state = "opponent_defend"
        print(card_game.opponent.hand)

        if card_game.turn <= 2:
            swap_index = card_game.opponent.choose_defense_swap(selected_exchange_card_index_opponent)
            if swap_index is not None:
                index = selected_exchange_card_index_opponent
                hovered_card_index_exchange = -1

                els_swap_cards_anim(1, index, swap_index)

                selected_exchange_card_index_opponent = index
                card_game.turn += 1
                card_game.state = "player_turn"
            else:
                els_user_take_from_opponent(selected_exchange_card_index_opponent)
                selected_exchange_card_index_opponent = -1
                hovered_card_index_exchange = -1
        else:
            els_user_take_from_opponent(selected_exchange_card_index_opponent)
            selected_exchange_card_index_opponent = -1
            hovered_card_index_exchange = -1

        print(card_game.opponent.hand)
        compute_hand_layout()

    def els_opponent_take_from_user(index):
        """Handle user taking a card from opponent during defense phase."""
        global selected_exchange_card_index_player, hovered_card_index
        take_card_anim(from_side=0, to_side=1, index=selected_exchange_card_index_player)
        card_game.turn = 1
        card_game.round += 1
        selected_exchange_card_index_player = -1
        hovered_card_index = -1
        card_game.state = "player_turn"
        renpy.jump("els_game_loop")

    def els_opponent_turn():
        """AI logic for opponent's turn."""
        global selected_exchange_card_index_player

        renpy.pause(1.5)

        selected_exchange_card_index_player = card_game.opponent_attack()

        if card_game.turn <= 2:
            card_game.state = "player_defend"
        else:
            els_opponent_take_from_user(selected_exchange_card_index_player)

        compute_hand_layout()

    # ----------------------------
    # Game result
    # ----------------------------
    def game_result_els():
        global result_combination_player
        global result_combination_indexes_player
        global result_combination_opponent
        global result_combination_indexes_opponent
        global selected_exchange_card_index_opponent
        global selected_exchange_card_index_player

        # Reset selections
        selected_exchange_card_index_opponent = -1
        selected_exchange_card_index_player = -1

        # Get final game result and combinations
        results = card_game.game_over()

        card_game.result = results[0]

        # Player combination: name and indexes
        result_combination_player = results[1][0].encode('utf-8').decode('unicode_escape')
        result_combination_indexes_player = results[1][3]
        print("Player combination: ", result_combination_player, result_combination_indexes_player)

        # Opponent combination: name and indexes
        result_combination_opponent = results[2][0].encode('utf-8').decode('unicode_escape')
        result_combination_indexes_opponent = results[2][3]
        print("Opponent combination: ", result_combination_opponent, result_combination_indexes_opponent)

        print("Game Over: ", card_game.result)

        renpy.pause(1.0)

        # Set game state
        card_game.state = "result"