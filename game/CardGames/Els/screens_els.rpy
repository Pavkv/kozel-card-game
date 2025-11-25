screen els():

    # Main game screen for els
    tag els_screen
    zorder 1

    if card_game.state not in ["player_turn", "player_defend", "player_give"]:
        timer 0.5 action Jump(card_game_name + "_game_loop")