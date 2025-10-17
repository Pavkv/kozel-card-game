init python:
    # ----------------------------
    # Player Turn Logic
    # ----------------------------
    def after_draw_player():
        if card_game.that_s_him and not persistent.achievements.get("Он самый", False):
            renpy.call_in_new_context("show_achievement", "Он самый", "that_s_him_message")
        if card_game.that_s_him and not persistent.achievements.get("Всё теперь на месте", False):
            renpy.call_in_new_context("show_achievement", "Всё теперь на месте", "all_in_place_message")
        if card_game.player.total21() >= 21:
            card_game.finalize()
        compute_hand_layout()
        renpy.jump("g21_game_loop")

    def g21_player_hit():
        draw_anim(side=0, target_count=len(card_game.player.hand) + 1, on_finish="after_draw_player")

    def g21_player_pass():
        if card_game.state == "player_turn" and card_game.result is None and card_game.first_player == card_game.player:
            card_game.state = "opponent_turn"
        else:
            card_game.finalize()
        renpy.jump("g21_game_loop")

    # ----------------------------
    # Opponent Turn Logic
    # ----------------------------
    def after_draw_opponent():
        if card_game.opponent.total21() >= 21:
            card_game.finalize()
        compute_hand_layout()
        renpy.jump("g21_game_loop")

    def g21_opponent_turn():
        renpy.pause(1.5)
        opponent_move = card_game.opponent_turn()
        print("Opponent move: ", opponent_move)
        if opponent_move == 'h':
            draw_anim(side=1, target_count=len(card_game.opponent.hand) + 1, on_finish="after_draw_opponent")
        elif opponent_move == 'p' and card_game.first_player == card_game.opponent:
            print("Opponent passes turn to player.")
            card_game.state = "player_turn"
        else:
            card_game.finalize()
        compute_hand_layout()
        renpy.jump("g21_game_loop")

    # ----------------------------
    # Animation Callbacks
    # ----------------------------
    def resolve_on_finish(key):
        if key == "after_draw_opponent":
            after_draw_opponent()
        elif key == "after_draw_player":
            after_draw_player()