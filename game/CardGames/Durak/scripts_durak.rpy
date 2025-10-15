label start_durak:
    $ player_name = renpy.input("Введите ваше имя", length=20)
    $ opponent_name = "Противник"
    $ cards_bg = "images/bg/bg_14.jpg"
    $ in_game = False
    $ base_card_img_src = "images/cards/cards"
    $ biased_draw = ["opponent", 0.5]
    $ day2_game_with_Alice = False
    $ last_winner = "player"
    $ start_card_game(DurakGame, "durak")

label durak_game_loop:
    $ print(card_game.player.hand)
    $ print(card_game.opponent.hand)

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
