label start:
    $ player_name = renpy.input("Введите ваше имя", length=20)
    $ opponent_name = "Противник"
    $ cards_bg = "images/bg/bg_14.jpg"
    $ in_game = False
    $ base_card_img_src = "images/cards/cards"
    $ biased_draw = ["opponent", 0.0]
    $ day2_game_with_Alice = False
    $ last_winner = "player"
    $ start_card_game(KozelGame, "kozel")

label kozel_game_loop:
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
        hide screen card_game_base_ui
        if in_game:
            jump expression card_game_results[card_game.result]
        else:
            $ reset_card_game()
            jump card_games

    call screen kozel
    jump kozel_game_loop
