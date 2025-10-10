screen kozel():

    # Main kozel game screen
    timer .5 action SetVariable("next_turn", False)
    if card_game.state not in ["player_attack", "player_defend"]:
         timer 5 action Jump(card_game_name + "_game_loop")

    # player taken cards
    use discard_pile_display_player()

    # opponent taken cards
    use discard_pile_display_opponent()

    # Table cards
    $ num_table_cards = len(card_game.table.table)
    $ max_table_width = 1280
    $ base_x = 320
    $ pair_spacing = min(200, max_table_width // max(1, num_table_cards))

    for i, (atk, (beaten, def_card)) in enumerate(card_game.table.table.items()):
        if atk not in in_flight_cards:
            $ atk_x = base_x + i * pair_spacing
            $ atk_y = 375

            if card_game.state == "player_defend" and not beaten:
                $ is_selected = selected_attack_card == atk
                imagebutton:
                    idle Transform(get_card_image(atk), xysize=(CARD_WIDTH, CARD_HEIGHT),
                                   yoffset=-20 if is_selected else 0,
                                   alpha=1.0 if is_selected else 0.9)
                    hover Transform(get_card_image(atk), xysize=(CARD_WIDTH, CARD_HEIGHT), yoffset=-20)
                    xpos atk_x
                    ypos atk_y
                    action SetVariable("selected_attack_card", atk)
            else:
                add Transform(get_card_image(atk), xysize=(CARD_WIDTH, CARD_HEIGHT)):
                    xpos atk_x
                    ypos atk_y

            if def_card:
                add Transform(get_card_image(def_card), xysize=(CARD_WIDTH, CARD_HEIGHT)):
                    xpos atk_x
                    ypos atk_y + 120

screen discard_pile_display_player():

    $ rotate = 0
    for card in card_game.player.discard:
        add Transform(base_cover_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=rotate + 15):
            xpos 50
            ypos 1080
        $ rotate += 5 if rotate < 45 else -45

screen discard_pile_display_opponent():

    $ rotate = 0
    for card in card_game.opponent.discard:
        add Transform(base_cover_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=rotate + 15):
            xpos 50
            ypos 0
        $ rotate += 5 if rotate < 45 else -45