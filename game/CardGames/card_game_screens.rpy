screen card_game_base_ui():
    tag base_ui
    zorder 0

    # Background
    add cards_bg xpos 0 ypos 0 xysize (1920, 1080)

    # Return to menu if not in-game
    if not in_game:
        frame:
            xpos 1755 ypos 750 xsize 150 padding (0, 0)
            has vbox
            textbutton "{color=#fff}Вернуться в меню{/color}":
                style "card_game_button"
                text_size 23
                action [
                    SetVariable("in_game", True),
                    Hide("card_game_base_ui"),
                    Jump("card_games")
                ]

    # Opponent Avatar & Info
    use opponent_info_block()

    # Game Phase & Action Buttons
    use game_phase_and_controls()

    # Trump and Deck Display
    use trump_and_deck_display()

    # Discard Pile
    use discard_pile_display()

    if not deal_cards:
        # Opponent Hand
        use opponent_card_hand_display()

        # Player Hand
        use player_card_hand_display()

    # Auto-jump after results
    if card_game.state == "result" or card_game.result:
        timer 0.5 action Jump(card_game_name + "_game_loop")

screen opponent_info_block():

    frame:
        background None
        xpos 1750
        ypos 20
        has vbox

        frame:
            background RoundRect("#b2b3b4", 10)
            xysize (150, 150)
            add opponent_avatar_displayable(size=(150, 150), pad=10) align (0.5, 0.5)

        frame:
            background RoundRect("#b2b3b4", 10)
            xsize 150
            yoffset 8
            padding (5, 5)
            text card_game.opponent.name color "#ffffff" text_align 0.5 align (0.5, 0.5)

        if day2_game_with_Alice:
            $ tournament_players = card_game.player.name + " | " + card_game.opponent.name
            $ tournament_scores = str(day2_alice_tournament_result[0]) + " | " + str(day2_alice_tournament_result[1])

            frame:
                background RoundRect("#b2b3b4", 10)
                xsize 150
                yoffset 18
                padding (2, 2)
                xalign 0.5
                yalign 0.0

                vbox:
                    spacing 4
                    xalign 0.5

                    text tournament_players color "#ffffff" size 19 xalign 0.5 text_align 0.5
                    text tournament_scores color "#ffffff" size 19 xalign 0.5 text_align 0.5

screen game_phase_and_controls():

    frame:
        background None
        xpos 1750
        ypos 823
        has vbox

        frame:
            background RoundRect("#b2b3b4", 10)
            xsize 150
            yoffset 10
            padding (5, 5)
            text "Фаза Игры:" color "#ffffff" text_align 0.5 align (0.5, 0.5)

        frame:
            background RoundRect("#b2b3b4", 10)
            xsize 150
            yoffset 20
            padding (5, 5)
            $ phase_text = "—"
            if card_game is not None and hasattr(card_game, "state"):
                $ phase_text = card_game_state_tl.get(card_game_name, {}).get(card_game.state, "—")

            text phase_text:
                color "#ffffff"
                size 19
                text_align 0.5
                align (0.5, 0.5)

        if isinstance(card_game, DurakGame) or isinstance(card_game, KozelGame):
            $ show_end_turn = card_game.table and card_game.state in ["player_turn", "player_defend"]
            $ show_confirm_attack = card_game.state == "player_turn" and len(selected_attack_card_indexes) > 0 or card_game.state == "player_drop" and len(selected_attack_card_indexes) == len(card_game.table.keys())
            if show_end_turn and show_confirm_attack:
                $ y1 = 30
                $ y2 = 40
            else:
                $ y1 = y2 = 30

            if show_end_turn:
                if card_game.state == "player_turn":
                    $ btn_text = "Бито"
                elif card_game.state == "player_defend" and isinstance(card_game, DurakGame):
                    $ btn_text = "Взять"
                elif card_game.state == "player_defend" and isinstance(card_game, KozelGame):
                    $ btn_text = "Сбросить"

                frame:
                    xsize 150
                    padding (0, 0)
                    ypos y1
                    has vbox
                    textbutton "{color=#fff}[btn_text]{/color}":
                        style "card_game_button"
                        text_size 25
                        action Function(handle_end_turn)

            if show_confirm_attack:
                if card_game.state == "player_turn":
                    $ btn_text = "Подтвердить\nатаку"
                elif card_game.state == "player_defend" and isinstance(card_game, DurakGame):
                    $ btn_text = "Подтвердить\nзащиту"
                elif card_game.state == "player_drop" and isinstance(card_game, KozelGame):
                    $ btn_text = "Подтвердить\nсброс"

                frame:
                    xsize 150
                    padding (0, 0)
                    ypos y2
                    has vbox
                    textbutton "{color=#fff}[btn_text]{/color}":
                        style "card_game_button"
                        text_size 18
                        action Function(eval("store." + handle_confirm_attack()))

        elif isinstance(card_game, WitchGame) and card_game.state == "wait_choice" and selected_exchange_card_index_opponent != -1:
            frame:
                xsize 150
                padding (0, 0)
                ypos 30
                has vbox
                textbutton "{color=#fff}Подтвердить{/color}":
                    style "card_game_button"
                    text_size 18
                    action [SetVariable("selected_exchange_card_index_opponent", -1), Function(take_card_anim, from_side=1, to_side=0, index=selected_exchange_card_index_opponent, on_finish=witch_after_exchange)]

        elif isinstance(card_game, ElsGame):
            if card_game.round < 5:
                frame:
                    background RoundRect("#b2b3b4", 10)
                    xsize 150
                    yoffset 5
                    ypos 20
                    padding (5, 5)
                    $ text = "Раунд {}/4 Обмен {}/2".format(card_game.round, card_game.turn)
                    text "[text]" color "#FFFFFF" text_align 0.5 align (0.5, 0.5)

            if card_game.state == "player_turn" and selected_exchange_card_index_opponent != -1:
                frame:
                    xsize 150
                    padding (0, 0)
                    ypos 30
                    has vbox
                    textbutton "{color=#fff}Подтвердить{/color}":
                        style "card_game_button"
                        text_size 18
                        action Function(els_swap_cards_opponent)

            if card_game.state == "player_defend" and selected_exchange_card_index_player != -1:
                frame:
                    xsize 150
                    padding (0, 0)
                    ypos 30
                    has vbox
                    textbutton "{color=#fff}Отдать карту{/color}":
                        style "card_game_button"
                        text_size 18
                        action Function(els_opponent_take_from_user, selected_exchange_card_index_player),

screen trump_and_deck_display():

    $ deck_text = str(len(card_game.deck.cards)) if len(card_game.deck.cards) > 0 else card_suits[card_game.deck.trump_suit]
    $ deck_num_xpos = DECK_NUM_X if len(card_game.deck.cards) > 9 else 73

    if card_game.deck.cards:

        if isinstance(card_game, DurakGame) or isinstance(card_game, KozelGame):

            $ trump = card_game.deck.trump_card
            if trump:
                add Transform(get_card_image(trump), xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=90):
                    xpos CARD_WIDTH // 2 - 55
                    ypos DECK_Y

        add Transform(base_cover_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=0):
            xpos DECK_X
            ypos DECK_Y

        text str(len(card_game.deck.cards)):
            xpos deck_num_xpos
            ypos DECK_NUM_Y
            size 60

    elif isinstance(card_game, DurakGame) and not card_game.deck.cards:
            text card_suits[card_game.deck.trump_suit]:
                xpos deck_num_xpos
                ypos DECK_NUM_Y
                size 75

screen discard_pile_display():

    $ rotate = 0
    for card in card_game.deck.discard:
        add Transform(base_cover_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=rotate + 15):
            xpos DISCARD_X
            ypos DISCARD_Y
        $ rotate += 15 if rotate < 360 else -360

screen opponent_card_hand_display():

    if isinstance(card_game, Game21) or isinstance(card_game, KozelGame) or (isinstance(card_game, ElsGame) and card_game.state == "result"):

        $ xpos = HAND_NUM_X
        $ ypos = OPPONENT_HAND_NUM_Y

        if isinstance(card_game, Game21):
            $ opponent_total = card_game.opponent.total21()
            $ opponent_hand_text = "Цена: " + (
                str(opponent_total) if card_game.state in ("reveal", "result")
                else "#" if opponent_total < 10
                else "##"
            )
        elif isinstance(card_game, KozelGame):
            $ opponent_hand_text = "Очки: " + str(card_game.opponent_points)
            $ xpos = 20

        else:
            $ opponent_hand_text = result_combination_opponent

        frame:
            background RoundRect("#b2b3b4", 10)
            xpos xpos
            ypos ypos
            xsize 150
            yoffset 10
            padding (5, 5)
            text "[opponent_hand_text]" color "#ffffff" text_align 0.5 align (0.5, 0.5)

    for i, card in enumerate(card_game.opponent.hand):

        if not card in in_flight_cards:
            $ card_x = opponent_card_layout[i]["x"]
            $ card_y = opponent_card_layout[i]["y"]
            $ is_hovered = (i == hovered_card_index_exchange)
            $ is_adjacent = abs(i - hovered_card_index_exchange) == 1

            $ x_shift = 20 if i == hovered_card_index_exchange + 1 else (-20 if i == hovered_card_index_exchange - 1 else 0)

            if isinstance(card_game, ElsGame) and card_game.state == "result":
                $ is_selected = (i in result_combination_indexes_opponent)
                $ y_shift = 80 if is_hovered or is_selected else 0
                imagebutton:
                    idle Transform(get_card_image(card), xysize=(CARD_WIDTH, CARD_HEIGHT))
                    hover Transform(get_card_image(card), xysize=(CARD_WIDTH, CARD_HEIGHT))
                    xpos card_x
                    ypos card_y
                    at hover_offset(y=y_shift, x=x_shift)

            elif (isinstance(card_game, Game21) or isinstance(card_game, WitchGame)) and card_game.state == "result" or card_game.result:
                add Transform(get_card_image(card), xysize=(CARD_WIDTH, CARD_HEIGHT)):
                    xpos card_x
                    ypos card_y

            elif (isinstance(card_game, WitchGame) and card_game.state == "wait_choice") or (isinstance(card_game, ElsGame) and card_game.state == "player_turn"):
                $ is_selected = (i == selected_exchange_card_index_opponent)
                $ y_shift = 80 if is_hovered or is_selected else 0
                imagebutton:
                    idle Transform(base_cover_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT))
                    hover Transform(base_cover_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT))
                    xpos card_x
                    ypos card_y
                    at hover_offset(y=y_shift, x=x_shift)
                    action If(
                        (isinstance(card_game, WitchGame) or isinstance(card_game, ElsGame)),
                        SetVariable("selected_exchange_card_index_opponent", i),
                        None
                    )
                    hovered If(hovered_card_index_exchange != i, SetVariable("hovered_card_index_exchange", i))
                    unhovered If(hovered_card_index_exchange == i, SetVariable("hovered_card_index_exchange", -1))

            else:
                add Transform(base_cover_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT)):
                    xpos card_x
                    ypos card_y

screen player_card_hand_display():

    if isinstance(card_game, Game21) or isinstance(card_game, KozelGame) or (isinstance(card_game, ElsGame) and card_game.state == "result"):

        $ xpos = HAND_NUM_X
        $ ypos = PLAYER_HAND_NUM_Y

        if isinstance(card_game, Game21):
            $ player_hand_text = "Цена: " + str(card_game.player.total21())

        elif isinstance(card_game, KozelGame):
            $ player_hand_text = "Очки: " + str(card_game.player_points)
            $ xpos = 20

        else:
            $ player_hand_text = result_combination_player

        frame:
            background RoundRect("#b2b3b4", 10)
            xpos xpos
            ypos ypos
            xsize 150
            padding (5, 5)
            text "[player_hand_text]" color "#ffffff" text_align 0.5 align (0.5, 0.5) size 25

    for i, card in enumerate(card_game.player.hand):

        if not card in in_flight_cards:
            $ card_x = player_card_layout[i]["x"]
            $ card_y = player_card_layout[i]["y"]
            $ is_hovered = (i == hovered_card_index)
            $ is_adjacent = abs(i - hovered_card_index) == 1
            $ x_shift = 20 if i == hovered_card_index + 1 else (-20 if i == hovered_card_index - 1 else 0)

            if isinstance(card_game, ElsGame) and card_game.state == "result":
                $ is_selected = (i in result_combination_indexes_player)
                $ y_shift = -80 if is_hovered or is_selected else 0
                imagebutton:
                    idle Transform(get_card_image(card), xysize=(CARD_WIDTH, CARD_HEIGHT))
                    hover Transform(get_card_image(card), xysize=(CARD_WIDTH, CARD_HEIGHT))
                    xpos card_x
                    ypos card_y
                    at hover_offset(y=y_shift, x=x_shift)

            else:
                $ is_selected = (i in selected_attack_card_indexes or i == selected_exchange_card_index_player)
                $ y_shift = -80 if is_hovered or is_selected else 0
                $ func_name, idx = handle_card_action(card_game, i)
                imagebutton:
                    idle Transform(get_card_image(card), xysize=(CARD_WIDTH, CARD_HEIGHT))
                    hover Transform(get_card_image(card), xysize=(CARD_WIDTH, CARD_HEIGHT))
                    xpos card_x
                    ypos card_y
                    at hover_offset(y=y_shift, x=x_shift)
                    if func_name:
                        action Function(eval("store." + func_name), idx)
                    hovered If(hovered_card_index != i, SetVariable("hovered_card_index", i))
                    unhovered If(hovered_card_index == i, SetVariable("hovered_card_index", -1))

screen table():
    timer .5 action SetVariable("next_turn", False)
    if card_game.state not in ["player_attack", "player_defend", "opponent_take"]:
         timer 5 action Jump(card_game_name + "_game_loop")

    $ num_table_cards = len(card_game.table.table)
    $ max_table_width = 1280
    $ base_x = 320
    $ pair_spacing = min(200, max_table_width // max(1, num_table_cards))

    for i, (atk, (beaten, def_card)) in enumerate(card_game.table.table.items()):
        if atk not in in_flight_cards:
            $ atk_x = base_x + i * pair_spacing
            $ atk_y = TABLE_Y

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
                    ypos atk_y + 115

screen deal_cards():

    for card_data in dealt_cards:

        $ i = card_data["index"]
        $ delay = card_data["delay"]

        if card_data["owner"] == "player":
            $ dest_x = player_card_layout[i]["x"]
            $ dest_y = player_card_layout[i]["y"]
            $ card_img_src = get_card_image(card_game.player.hand[i])
        else:
            $ dest_x = opponent_card_layout[i]["x"]
            $ dest_y = opponent_card_layout[i]["y"]
            $ card_img_src = base_cover_img_src

        add Transform(card_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT)) at deal_card(dest_x, dest_y, delay)

    timer delay + 1.0 action Jump(card_game_name + "_game_loop")

screen table_card_animation(on_finish=None, args=(), kwargs={}, delay=0.0):

    default max_duration = delay

    for anim in table_animations:
        $ card = anim["card"]
        $ src_x = anim["src_x"]
        $ src_y = anim["src_y"]
        $ dest_x = anim["dest_x"]
        $ dest_y = anim["dest_y"]
        $ delay = anim["delay"]
        $ duration = anim.get("duration", 0.4)
        $ anim_time = delay + duration

        $ in_flight_cards.add(card)
        $ max_duration = max(max_duration, anim_time)

        add Transform(
            anim.get("override_img", get_card_image(card)),
            xysize=(CARD_WIDTH, CARD_HEIGHT)
        ) at animate_table_card(src_x, src_y, dest_x, dest_y, delay, duration)

        timer anim_time action Function(in_flight_cards.discard, card)

    timer max_duration + 0.01 action [
        SetVariable("table_animations", []),
        SetVariable("in_flight_cards", set()),
        Function(renpy.restart_interaction),
        Hide("table_card_animation"),
        Function(resolve_on_finish, on_finish, args, kwargs) if on_finish else None
    ]