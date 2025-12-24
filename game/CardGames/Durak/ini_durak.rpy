init python:
    # Card selection and layout state
    confirm_attack = False
    confirm_take = False
    selected_card = None
    selected_attack_card = None
    attack_target = None
    can_pass = False
    passed = False
    durak_full_throw = None
    durak_passing = False
    confirm_turn = [False, False]

    # Turn and animation state
    durak_draw_animations_dict = {
        0: "durak_player_draw",
        1: "durak_opponent_draw",
        2: "durak_opponent_2_draw",
        3: "durak_opponent_3_draw",
    }

    # Opponent defense turn
    opponent_defense_queue = []
    opponent_defense_index = 0

    # Achievements
    lost_to_two_sixes = False
    last_attack_two_sixes = True
    sixes_loss_candidate = False