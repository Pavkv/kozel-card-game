label start:
    $ player_name = renpy.input("Введите ваше имя", length=20)
    $ opponent_name = "Противник"
    $ cards_bg = "images/bg/bg_14.jpg"
    $ in_game = False
    $ base_card_img_src = "images/cards/cards"
    $ biased_draw = ["opponent", 0.5]
    $ day2_game_with_Alice = False
    $ last_winner = "player"
    $ start_card_game(WitchGame, "witch")

label witch_game_loop:
    $ print(card_game.player.hand)
    $ print(card_game.opponent.hand)
    if is_dealing:
#         $ renpy.block_rollback()
        $ is_dealing = False
        call screen deal_cards
    else:
        $ deal_cards = False

    $ print(card_game.user_turn)

    if card_game.state == "result":
#       $ renpy.block_rollback()
        if in_game and card_game.result != player_name:
            $ renpy.call_in_new_context("show_achievement", "Да ты ведьма!", "you_are_a_witch_message")
        $ renpy.jump("card_game_result_handler")

    if card_game.state == "opponent_turn":
#         $ renpy.block_rollback()
        pause 1.5
        $ witch_opponent_turn()

    call screen witch
    jump witch_game_loop


