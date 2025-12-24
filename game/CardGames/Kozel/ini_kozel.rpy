init python:
    confirm_drop = False
    drop_queue = []
    drop_index = 0
    draw_up_to_hand_size = 0
    
    # Turn and animation state
    kozel_draw_animations_dict = {
        0: "kozel_player_draw",
        1: "kozel_opponent_draw",
        2: "kozel_opponent_2_draw",
        3: "kozel_opponent_3_draw",
    }

    # Discard pile positions
    KOZEL_PLAYERS_X = 50
    KOZEL_DISCARD_X_SPACING = 180
    KOZEL_PLAYER_DISCARD_Y = 800
    KOZEL_OPPONENT_DISCARD_Y = 0

    #achievements
    same_suit_achievement = False
    all_trumps_achievement = False
    three_aces_achievement = False
    three_sixes_achievement = False