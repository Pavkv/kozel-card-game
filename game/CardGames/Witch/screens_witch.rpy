screen witch():

    # Main game screen for witch
    tag witch_screen
    zorder 1

    if card_game.state not in ["wait_choice", "player_turn"]:
         timer 0.5 action Jump(card_game_name + "_game_loop")
    else:
        frame:
            background None
            xpos 1750
            ypos 945
            has vbox
            if card_game.user_turn == "draw":
                frame:
                    xsize 150
                    padding (0, 0)
                    ypos 30
                    has vbox
                    textbutton "{color=#fff}Взять{/color}":
                        style "card_game_button"
                        text_size 25
                        action Function(draw_anim, side=0, target_count=6, on_finish=witch_after_draw)

            elif card_game.user_turn == "discard_pairs":
                frame:
                    xsize 150
                    padding (0, 0)
                    has vbox
                    textbutton "{color=#fff}Скинуть\nпары{/color}":
                        style "card_game_button"
                        text_size 18
                        action Function(discard_pairs_anim, side=0, on_finish=witch_after_discard)

            elif card_game.user_turn == "exchange" and not made_turn:
                frame:
                    xsize 150
                    padding (0, 0)
                    has vbox
                    textbutton "{color=#fff}Вытянуть\nкарту{/color}":
                        style "card_game_button"
                        text_size 18
                        action [
                            SetVariable("card_game.state", "wait_choice"),
                            SetVariable("card_game.user_turn", None),
                            SetVariable("made_turn", True)
                        ]

            elif card_game.user_turn == "end_turn":
                timer 0.5 action Function(witch_end_player_turn)