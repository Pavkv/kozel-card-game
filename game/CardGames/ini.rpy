init python:
    # init
    card_game = None
    card_game_name = None
    player_name = None
    opponent_name = None
    base_card_img_src = None
    base_cover_img_src = None
    cards_bg = None
    in_game = True
    card_game_results = {}
    card_game_avatar = None
    biased_draw = None
    made_turn = False
    last_winner = None

    CARD_WIDTH, CARD_HEIGHT, CARD_SPACING = 157, 237, 118
    suits = {'C': 'uvao', 'D': '2ch', 'H': 'ussr', 'S': 'utan'}
    ranks = {'6': '6', '7': '7', '8': '8', '9': '9', '10': '10', 'J': '11', 'Q': '12', 'K': '13', 'A': '1'} # '2': '2', '3': '3', '4': '4', '5': '5',

    # Layout constants
    DECK_X = -50
    DECK_Y = 422
    DECK_NUM_X = 55
    DECK_NUM_Y = 527
    DISCARD_X = 1600
    DISCARD_Y = 422
    TABLE_Y = 383
    PLAYER_HAND_X = 700
    PLAYER_HAND_Y = 825
    PLAYER_HAND_NUM_Y = 703
    OPPONENT_HAND_X = 700
    OPPONENT_HAND_Y = 20
    OPPONENT_HAND_NUM_Y = 377
    HAND_SPACING = 118
    HAND_NUM_X = 885

    # Card selection and layout state
    hovered_card_index = -1
    hovered_card_index_exchange = -1
    selected_card_indexes = set()
    selected_attack_card_indexes = set()
    selected_exchange_card_index_player = -1
    selected_exchange_card_index_opponent = -1

    # Turn and animation state
    deal_cards = True
    next_turn = True
    dealt_cards = []
    is_dealing = False
    draw_animations = []
    is_drawing = False
    table_animations = []
    is_table_animating = False
    in_flight_cards = set()

    # Card layouts
    player_card_layout = []
    opponent_card_layout = []

    # Suit translations
    card_suits = {
        "C": "К",
        "D": "Б",
        "H": "Ч",
        "S": "П"
    }

    # Game phase translations
    card_game_state_tl = {
        "els": {
            "player_turn": "Вы вытягиваете",
            "player_defend": "Вы защищаетесь",
            "opponent_turn": "Противник вытягивает",
            "opponent_defend": "Противник защищается",
            "wait_choice": "Вытягивание карты",
            "wait_choice_opponent": "Противник вытягивает карту",
            "results": "Игра окончена"
        },
        "durak" : {
            "player_turn": "Вы атакуете",
            "player_defend": "Вы защищаетесь",
            "player_take": "Вы берёте",
            "opponent_turn": "Противник атакует",
            "opponent_defend": "Противник защищается",
            "opponent_take": "Противник берёт",
            "end_turn": "Окончание хода",
            "results": "Игра окончена"
        },
        "g21": {
            "initial_deal": "Раздача",
            "player_turn": "Ваш ход",
            "opponent_turn": "Ход противника",
            "reveal": "Раскрытие",
            "results": "Игра окончена"
        },
        "witch": {
            "player_turn": "Ваш ход",
            "opponent_turn": "Ход противника",
            "opponent_busy": "Ход противника",
            "wait_choice": "Вытягивание карты",
            "wait_choice_opponent": "Противник вытягивает карту",
            "results": "Игра окончена"
        },
        "kozel" : {
            "player_turn": "Вы атакуете",
            "player_defend": "Вы защищаетесь",
            "player_drop": "Вы сбрасываете",
            "opponent_turn": "Противник атакует",
            "opponent_defend": "Противник защищается",
            "opponent_drop": "Противник сбрасывает",
            "end_turn": "Окончание хода",
            "results": "Игра окончена"
        },
    }

# Card transforms
transform hover_offset(y=0, x=0):
    easein 0.1 yoffset y xoffset x

transform no_shift:
    xoffset 0
    yoffset 0

transform deal_card(dest_x, dest_y, delay=0):
    alpha 0.0
    xpos DECK_X
    ypos DECK_Y
    pause delay
    linear 0.3 alpha 1.0 xpos dest_x ypos dest_y

transform animate_table_card(x1, y1, x2, y2, delay=0.0, duration=0.4):
    alpha 1.0
    anchor (0, 0)
    xanchor 0
    xpos x1
    ypos y1
    pause delay

    linear duration xpos x2 ypos y2 alpha 0

# Styles
style card_game_button:
    background RoundRect("#b2b3b4", 10)
    hover_background RoundRect("#757e87", 10)
    xsize 150
    padding (5, 5)
    text_align 0.5
    align (0.5, 0.5)

# Game result handler
label card_game_result_handler:
    $ renpy.pause(3.0, hard=True)
    hide screen card_game_base_ui

    if in_game:
        $ result = card_game.result
        $ enable_ingame_controls()
        $ reset_card_game()
        jump expression card_game_results[result]
    else:
        if card_game.result == card_game.player.name:
            "Вы выиграли!"
        elif card_game.result == card_game.opponent.name:
            "Вы проиграли."
        else:
            "Ничья."
        jump ga_play_again

# Show Achievements
label show_achievement(key, message_tag):
    play sound sfx_achievement
    show expression message_tag at achievement_trans
    with dspr
    $ renpy.pause(3, hard=True)
    hide expression message_tag
    $ persistent.achievements[key] = True
    return