label start_durak:
#     "Выберите количество противников"
#     menu:
#         "Один противник":
#             $ number_of_opponents = 1
#         "Два противника":
#             $ number_of_opponents = 2
#         "Три противника":
#             $ number_of_opponents = 3
#     "Использовать полную колоду?"
#     menu:
#         "Да":
#             $ use_full_deck = True
#         "Нет":
#             $ use_full_deck = False
#     "Переводы разрешены?"
#     menu:
#         "Да":
#             $ durak_passing = True
#         "Нет":
#             $ durak_passing = False
#     "До завала?"
#     menu:
#         "Да":
#             $ durak_full_throw = True
#         "Нет":
#             $ durak_full_throw = False
#     $ player_name = "Pasha"
#     $ opponent_name = "Противник"
#     $ cards_bg = "images/bg/bg_14.jpg"
#     $ in_game = False
#     $ base_card_img_src = "images/cards/cards"
#     $ biased_draw = ["opponent", 0.0]
#     $ day2_game_with_Alice = False
#     $ last_winner = "player"
#     $ use_full_deck = False
#     $ durak_passing = True
#     $ durak_full_throw = True
#     $ number_of_opponents = 3
    $ start_card_game(DurakGame, "durak", game_kwargs={"full_deck": use_full_deck, "full_throw": durak_full_throw, "can_pass": durak_passing, "number_of_opponents": number_of_opponents})

label durak_game_loop:
    if len(card_game.current_defender) == 0:
        $ card_game.state = "end_turn"

    if is_dealing:
#         $ renpy.block_rollback()
        $ is_dealing = False
        call screen deal_cards
    else:
        $ deal_cards = False

    if card_game.result:
#         $ renpy.block_rollback()
        $ print("Game Over: ", card_game.result)
        $ card_game.state = "result"

    if card_game.state in ["opponent_turn", "player_take"]:
#         $ renpy.block_rollback()
        $ durak_opponent_turn()

    elif card_game.state == "opponent_defend":
#         $ renpy.block_rollback()
        $ durak_opponent_defend()

    elif card_game.state == "end_turn":
#         $ renpy.block_rollback()
        $ durak_end_turn()

    if card_game.state == "result":
#       $ renpy.block_rollback()
        if card_game.result == card_game.opponent.name and lost_to_two_sixes:
            $ renpy.call_in_new_context("show_achievement", "Адмирал", "admiral_message")
        $ renpy.jump("card_game_result_handler")

    call screen durak
    jump durak_game_loop
