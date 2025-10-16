init python:
    # ----------------------------
    # User Turn Logic
    # ----------------------------
    def witch_after_draw():
        """Call this after player has pressed the 'draw' button and animation finishes."""
        global made_turn
        compute_hand_layout()

        game_over_check()

        if card_game.player.count_pairs_excluding_witch() > 0:
            card_game.user_turn = "discard_pairs"
        elif card_game.player.can_exchange_now(card_game.deck) and len(card_game.opponent.hand) > 0 and not made_turn:
            card_game.user_turn = "exchange"
        else:
            card_game.user_turn = "end_turn"

    def witch_after_discard():
        """Call this after player has pressed 'discard_pairs' and animation finishes."""
        global made_turn
        compute_hand_layout()

        game_over_check()

        if card_game.player.can_exchange_now(card_game.deck) and len(card_game.opponent.hand) > 0 and not made_turn:
            card_game.user_turn = "exchange"
        else:
            card_game.user_turn = "end_turn"

    def witch_after_exchange():
        """Call this after player has selected and taken a card from opponent."""
        compute_hand_layout()

        game_over_check()

        if card_game.player.count_pairs_excluding_witch() > 0:
            card_game.user_turn = "discard_pairs"
        else:
            card_game.user_turn = "end_turn"

    def witch_end_player_turn():
        """Call this when player presses 'end_turn' button or finishes last action."""
        global made_turn
        game_over_check()
        made_turn = False
        card_game.state = "opponent_turn"
        compute_hand_layout()

    # ----------------------------
    # Opponent Turn Logic
    # ----------------------------
    def witch_opponent_end_turn():
        game_over_check()
        print("AI ends turn.")
        card_game.state = "player_turn"
        card_game.player_turn_start()
        compute_hand_layout()

    def witch_opponent_after_draw():
        compute_hand_layout()
        game_over_check()
        if card_game.opponent.count_pairs_excluding_witch() > 0:
            discard_pairs_anim(side=1, on_finish="witch_opponent_end_turn")
        elif card_game.opponent.can_exchange_now(card_game.deck):
            witch_opponent_maybe_exchange()
        else:
            show_anim(on_finish="witch_opponent_end_turn")

    def witch_opponent_after_discard():
        game_over_check()
        if card_game.opponent.can_exchange_now(card_game.deck):
            witch_opponent_maybe_exchange()
        else:
            show_anim(on_finish="witch_opponent_end_turn")

    def witch_opponent_after_exchange():
        game_over_check()
        if card_game.opponent.count_pairs_excluding_witch() > 0:
            discard_pairs_anim(side=1, on_finish="witch_opponent_end_turn")
        else:
            show_anim(on_finish="witch_opponent_end_turn")

    def witch_opponent_maybe_exchange():
        game_over_check()
        print("AI attempts to exchange a card.")
        if len(card_game.player.hand) == 0:
            print("User has no cards, AI skips exchange.")
            show_anim(on_finish="witch_opponent_end_turn")
        else:
            card_game.state = "wait_choice_opponent"
            index = card_game.opponent.choose_exchange_index(card_game.player)
            take_card_anim(
                from_side=0,
                to_side=1,
                index=index,
                on_finish="witch_opponent_after_exchange"
            )

    def witch_opponent_turn():
        """AI turn logic for Witch game using named callbacks and show_anim-style logic."""
        game_over_check()
        card_game.state = "opponent_busy"

        if len(card_game.opponent.hand) < 6 and len(card_game.deck.cards) > 0:
            print("AI draws cards.")
            draw_anim(
                side=1,
                target_count=6,
                on_finish="witch_opponent_after_draw"
            )
        elif card_game.opponent.count_pairs_excluding_witch() > 0:
            print("AI has pairs to discard.")
            discard_pairs_anim(
                side=1,
                on_finish="witch_opponent_after_discard"
            )
        elif card_game.opponent.can_exchange_now(card_game.deck):
            print("AI can exchange a card.")
            witch_opponent_maybe_exchange()
        else:
            print("AI has nothing to do, ends turn.")
            show_anim(on_finish="witch_opponent_end_turn")

    # Function dispatcher for animations
    def resolve_on_finish(key, *args, **kwargs):
        if key == "witch_opponent_after_draw":
            witch_opponent_after_draw()
        elif key == "witch_opponent_after_discard":
            witch_opponent_after_discard()
        elif key == "witch_opponent_after_exchange":
            witch_opponent_after_exchange()
        elif key == "witch_opponent_end_turn":
            witch_opponent_end_turn()
        elif key == "witch_opponent_maybe_exchange":
            witch_opponent_maybe_exchange()
        elif key == "delay_anim":
            final = kwargs.get("on_finish")
            delay_anim(on_finish=final)

    # ----------------------------
    # Game Over
    # ----------------------------
    def game_over_check():
        """Check if the game is over and handle the result."""
        game_over = card_game.game_over()
        if game_over[0]:
            card_game.result = game_over[1]
            print("Game Over: ", card_game.result)
            card_game.state = "result"
            renpy.jump("witch_game_loop")
