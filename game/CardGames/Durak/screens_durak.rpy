screen durak():

    if card_game.table.beaten() and card_game.state == "player_defend":
        timer .5 action SetVariable("card_game.state", "opponent_turn")

    if card_game.state == "opponent_take" and not card_game.can_attack(card_game.player):
        timer 1.5 action SetVariable("card_game.state", "end_turn")

    use table()
