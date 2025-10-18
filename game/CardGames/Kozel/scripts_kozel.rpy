label start:
    $ player_name = renpy.input("Введите ваше имя", length=20)
    $ opponent_name = "Противник"
    $ cards_bg = "images/bg/bg_14.jpg"
    $ in_game = False
    $ base_card_img_src = "images/cards/cards"
    $ biased_draw = ["opponent", 1]
    $ day2_game_with_Alice = False
    $ last_winner = "player"
    $ start_card_game(KozelGame, "kozel")

label kozel_game_loop:
    $ print(card_game.player.hand)
    $ print(card_game.opponent.hand)

    if card_game.same_suit():
        $ kozel_same_suit_achievement = True

    if card_game.all_trumps():
        $ kozel_all_trumps_achievement = True

    if card_game.three_aces():
        $ kozel_three_aces_achievement = True

    if card_game.three_sixes():
        $ kozel_three_sixes_achievement = True

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

    if card_game.state == "opponent_turn":
#         $ renpy.block_rollback()
        $ kozel_opponent_turn()

    elif card_game.state == "opponent_defend":
#         $ renpy.block_rollback()
        $ kozel_opponent_defend()

    elif card_game.state == "end_turn":
#         $ renpy.block_rollback()
        $ kozel_end_turn()

    if card_game.state == "result":
#       $ renpy.block_rollback()
        if in_game and kozel_same_suit_achievement:
            $ renpy.call_in_new_context("show_achievement", "Письмо", "letter_message")
        if in_game and kozel_all_trumps_achievement:
            $ renpy.call_in_new_context("show_achievement", "Бура", "bura_message")
        if in_game and kozel_three_aces_achievement:
            $ renpy.call_in_new_context("show_achievement", "Москва", "moscow_message")
        if in_game and kozel_all_trumps_achievement:
            $ renpy.call_in_new_context("show_achievement", "Малая Москва", "small_moscow_message")
        $ renpy.jump("card_game_result_handler")

    call screen kozel
    jump kozel_game_loop
