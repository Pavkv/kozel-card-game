screen durak():

    if card_game.table.beaten() and card_game.state == "player_defend":
        timer .5 action SetVariable("card_game.state", "opponent_turn")

    use table()
