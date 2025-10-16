label start_els:
    $ player_name = renpy.input("Введите ваше имя", length=20)
    $ opponent_name = "Противник"
    $ cards_bg = "images/bg/bg_14.jpg"
    $ in_game = False
    $ base_card_img_src = "images/cards/cards"
    $ biased_draw = ["opponent", 0.5]
    $ day2_game_with_Alice = False
    $ last_winner = "player"
    $ start_card_game(ElsGame, "els")

label els_game_loop:
    if is_dealing:
#         $ renpy.block_rollback()
        $ is_dealing = False
        call screen deal_cards
    else:
        $ deal_cards = False

    if card_game.round == 5:
#         $ renpy.block_rollback()
        $ game_result_els()

    if card_game.state == "result":
#       $ renpy.block_rollback()
        $ renpy.jump("card_game_result_handler")

    if card_game.state == "opponent_turn":
#         $ renpy.block_rollback()
        $ els_opponent_turn()

    call screen els
    jump els_game_loop


