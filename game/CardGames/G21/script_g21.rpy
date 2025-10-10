label start_g21:
    $ start_card_game(Game21, "g21", game_kwargs={"initial_deal": g21_card_num, "aces_low": g21_aces_low})

label g21_game_loop:
    if is_dealing:
#         $ renpy.block_rollback()
        $ is_dealing = False
        call screen deal_cards
    else:
        $ deal_cards = False

    if card_game.state == "result":
#       $ renpy.block_rollback()
        if card_game.result == player_name and card_game.player.total21() == 21 and ['7', 'Q', 'A'] in card_game.player.get_ranks():
            $ renpy.call_in_new_context("show_achievement", "Три карты", "three_cards_message")
        if card_game.result == player_name and card_game.player.total21() == 21 and ['7', '7', '7'] == card_game.player.get_ranks():
            $ renpy.call_in_new_context("show_achievement", "Три топора", "three_axes_message")
        $ renpy.jump("card_game_result_handler")

    if card_game.result:
#         $ renpy.block_rollback()
        $ print("Game Over: ", card_game.result)
        $ card_game.state = "result"

    if card_game.state == "opponent_turn":
#         $ renpy.block_rollback()
        $ g21_opponent_turn()

    call screen game21
    jump g21_game_loop


