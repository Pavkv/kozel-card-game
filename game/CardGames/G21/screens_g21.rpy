screen game21():

    # Main game screen for 21
    tag game21_screen
    zorder 1

    if card_game.state != "player_turn" or card_game.result is not None:
         timer 0.5 action Jump(card_game_name + "_game_loop")
    else:
        frame:
            background None
            xpos 1750
            ypos 945

            frame:
                xsize 150
                padding (0, 0)
                has vbox
                textbutton "{color=#fff}Взять{/color}":
                    style "card_game_button"
                    text_size 25
                    action Function(g21_player_hit)

            frame:
                xsize 150
                padding (0, 0)
                ypos 50
                has vbox
                textbutton "{color=#fff}Пас{/color}":
                    style "card_game_button"
                    text_size 25
                    action Function(g21_player_pass)